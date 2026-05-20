from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.auth.jwt import create_access_token
from backend.auth.service import start_auth, verify_auth
from backend.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


class PhoneStartRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$")


class PhoneStartResponse(BaseModel):
    status: str
    dev_code: str | None = None


class PhoneVerifyRequest(BaseModel):
    phone: str
    code: str


class PhoneVerifyResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    phone: str
    draft_intake_case_id: str | None = None


@router.post("/phone/start", response_model=PhoneStartResponse)
def start_phone_auth(payload: PhoneStartRequest) -> PhoneStartResponse:
    code = start_auth(payload.phone)
    if settings.TEST_SMS_CODE:
        return PhoneStartResponse(status="dev_code_returned", dev_code=code)
    return PhoneStartResponse(status="sent", dev_code=None)


@router.post("/phone/verify", response_model=PhoneVerifyResponse)
def verify_phone_auth(payload: PhoneVerifyRequest) -> PhoneVerifyResponse:
    is_valid = verify_auth(payload.phone, payload.code)
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid or expired code")

    access_token = create_access_token(payload.phone)

    try:
        from backend.intake.store import find_draft_by_phone

        draft_id = find_draft_by_phone(payload.phone)
    except Exception:
        draft_id = None

    return PhoneVerifyResponse(
        access_token=access_token,
        phone=payload.phone,
        draft_intake_case_id=draft_id,
    )
