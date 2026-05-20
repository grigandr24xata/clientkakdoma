from fastapi import APIRouter
from pydantic import BaseModel

from backend.dedup.service import dedup_resident, dedup_within_intake

router = APIRouter(prefix="/dedup", tags=["dedup"])


class DedupCheckRequest(BaseModel):
    ocr_data: dict


class DedupIntakeCheckRequest(BaseModel):
    residents_ocr_data: list[dict]


@router.post("/check")
def check_resident_dedup(payload: DedupCheckRequest) -> dict:
    result = dedup_resident(payload.ocr_data)
    return {
        "match_type": result.match_type,
        "client_id": result.client.id if result.client else None,
        "manual_check": result.manual_check,
        "reason": result.reason,
    }


@router.post("/check-intake")
def check_intake_dedup(payload: DedupIntakeCheckRequest) -> dict:
    duplicate_hashes = dedup_within_intake(payload.residents_ocr_data)
    return {
        "duplicate_hashes": duplicate_hashes,
        "has_duplicates": len(duplicate_hashes) > 0,
    }
