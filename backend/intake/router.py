from dataclasses import asdict

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel, Field

from backend.auth.deps import get_current_phone
from backend.intake import store
from backend.files.store import FileRecord, get_files_for_case, save_file_record
from backend.intake.models import IntakeBranch, IntakeCase, IntakeResident
from backend.intake.ocr_flow import handle_passport_upload

router = APIRouter(prefix="/intake", tags=["intake"])


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
ALLOWED_EXTRA_DOC_TYPES = {"migration_card", "patent", "work_contract", "other"}
MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024


class CaseCreateRequest(BaseModel):
    branch: IntakeBranch


class BranchUpdateRequest(BaseModel):
    branch: IntakeBranch


class ResidentsCountUpdateRequest(BaseModel):
    resident_count: int = Field(ge=1, le=25)


class ResidentOcrUpdateRequest(BaseModel):
    ocr_data: dict
    confirmed: bool


class ResidentPhoneUpdateRequest(BaseModel):
    phone: str


def _get_owned_case(case_id: str, current_phone: str) -> IntakeCase:
    case = store.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.phone != current_phone:
        raise HTTPException(status_code=403, detail="Forbidden")
    return case


@router.post("/cases", response_model=IntakeCase)
def create_case(payload: CaseCreateRequest, current_phone: str = Depends(get_current_phone)) -> IntakeCase:
    existing_case_id = store.find_draft_by_phone(current_phone)
    if existing_case_id:
        existing_case = store.get_case(existing_case_id)
        if existing_case:
            return existing_case

    case = store.create_case(current_phone)
    case.branch = payload.branch
    case.residents = [IntakeResident(order_index=1, is_main=True, phone=current_phone)]
    case.step = "branch_selected"
    return store.update_case(case)


@router.get("/cases/{case_id}", response_model=IntakeCase)
def get_case(case_id: str, current_phone: str = Depends(get_current_phone)) -> IntakeCase:
    return _get_owned_case(case_id, current_phone)


@router.patch("/cases/{case_id}/branch", response_model=IntakeCase)
def patch_case_branch(
    case_id: str,
    payload: BranchUpdateRequest,
    current_phone: str = Depends(get_current_phone),
) -> IntakeCase:
    case = _get_owned_case(case_id, current_phone)
    case.branch = payload.branch
    return store.update_case(case)


@router.patch("/cases/{case_id}/residents/count", response_model=IntakeCase)
def patch_residents_count(
    case_id: str,
    payload: ResidentsCountUpdateRequest,
    current_phone: str = Depends(get_current_phone),
) -> IntakeCase:
    case = _get_owned_case(case_id, current_phone)
    case.resident_count = payload.resident_count

    existing_indexes = {resident.order_index for resident in case.residents}
    for idx in range(1, payload.resident_count + 1):
        if idx not in existing_indexes:
            case.residents.append(IntakeResident(order_index=idx, is_main=(idx == 1), phone=current_phone if idx == 1 else None))

    case.residents.sort(key=lambda resident: resident.order_index)
    case.step = "residents_count_set"
    return store.update_case(case)


@router.patch("/cases/{case_id}/residents/{order_index}/ocr", response_model=IntakeCase)
def patch_resident_ocr(
    case_id: str,
    order_index: int,
    payload: ResidentOcrUpdateRequest,
    current_phone: str = Depends(get_current_phone),
) -> IntakeCase:
    case = _get_owned_case(case_id, current_phone)
    resident = next((r for r in case.residents if r.order_index == order_index), None)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    resident.ocr_data = payload.ocr_data
    resident.ocr_confirmed = payload.confirmed

    if payload.confirmed:
        unconfirmed = [r for r in sorted(case.residents, key=lambda r: r.order_index) if not r.ocr_confirmed]
        if unconfirmed:
            case.step = f"ocr_confirm_{unconfirmed[0].order_index}"
        else:
            case.step = "extra_docs"

    return store.update_case(case)


@router.patch("/cases/{case_id}/residents/{order_index}/phone", response_model=IntakeCase)
def patch_resident_phone(
    case_id: str,
    order_index: int,
    payload: ResidentPhoneUpdateRequest,
    current_phone: str = Depends(get_current_phone),
) -> IntakeCase:
    case = _get_owned_case(case_id, current_phone)
    resident = next((r for r in case.residents if r.order_index == order_index), None)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    resident.phone = payload.phone
    return store.update_case(case)


@router.post("/cases/{case_id}/submit", response_model=IntakeCase)
def submit_case(case_id: str, current_phone: str = Depends(get_current_phone)) -> IntakeCase:
    case = _get_owned_case(case_id, current_phone)
    if any(not resident.ocr_confirmed for resident in case.residents):
        raise HTTPException(status_code=400, detail="All residents must be OCR-confirmed")

    case.status = "submitted"
    case.step = "submitted"
    return store.update_case(case)


@router.get("/cases", response_model=list[IntakeCase])
def list_cases(current_phone: str = Depends(get_current_phone)) -> list[IntakeCase]:
    return store.list_cases_by_phone(current_phone)


@router.post("/cases/{case_id}/residents/{order_index}/passport")
async def upload_passport(
    case_id: str,
    order_index: int,
    file: UploadFile = File(...),
    current_phone: str = Depends(get_current_phone),
) -> dict:
    case = _get_owned_case(case_id, current_phone)
    if order_index < 1 or order_index > case.resident_count:
        raise HTTPException(status_code=400, detail="Invalid resident order index")

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Only image/jpeg and image/png are supported")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_UPLOAD_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File is too large. Maximum allowed size is 10MB")

    return await handle_passport_upload(
        intake_case_id=case.id,
        resident_order_index=order_index,
        image_bytes=image_bytes,
        content_type=file.content_type or "application/octet-stream",
        original_filename=file.filename or "passport",
    )


@router.post("/cases/{case_id}/extra-docs")
async def upload_extra_doc(
    case_id: str,
    file: UploadFile = File(...),
    file_type: str = Query(...),
    resident_order_index: int | None = Query(default=None),
    current_phone: str = Depends(get_current_phone),
) -> dict:
    case = _get_owned_case(case_id, current_phone)

    if file_type not in ALLOWED_EXTRA_DOC_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file_type")

    if resident_order_index is not None and (resident_order_index < 1 or resident_order_index > case.resident_count):
        raise HTTPException(status_code=400, detail="Invalid resident order index")

    file_bytes = await file.read()
    file_record = FileRecord(
        intake_case_id=case.id,
        resident_order_index=resident_order_index,
        file_type=file_type,
        original_filename=file.filename or "document",
        content_type=file.content_type or "application/octet-stream",
        size_bytes=len(file_bytes),
        storage_key=f"intake/{case.id}/extra/{file_type}/{file.filename or 'document'}",
        storage_url=f"stub://intake/{case.id}/extra/{file_type}/{file.filename or 'document'}",
    )
    save_file_record(file_record)

    return {"file_id": file_record.id, "file_type": file_record.file_type, "status": "uploaded"}


@router.get("/cases/{case_id}/files")
def get_case_files(case_id: str, current_phone: str = Depends(get_current_phone)) -> list[dict]:
    _get_owned_case(case_id, current_phone)
    return [asdict(file_record) for file_record in get_files_for_case(case_id)]
