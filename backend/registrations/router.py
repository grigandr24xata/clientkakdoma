from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.apartments.store import get_apartment
from backend.registrations.models import Registration, RegistrationStatus
from backend.registrations.service import add_registration, refresh_registration_statuses
from backend.registrations.store import (
    get_registration,
    list_all_registrations,
    list_registrations_by_apartment,
    list_registrations_by_deal,
    update_registration,
)

router = APIRouter(prefix="/registrations", tags=["registrations"])


class RegistrationCreate(BaseModel):
    deal_id: str
    client_id: str
    apartment_id: str
    date_start: date
    date_end: date


class MfcDocUpdate(BaseModel):
    mfc_doc_url: str


@router.get("/")
def list_registrations() -> list[Registration]:
    refresh_registration_statuses()
    return list_all_registrations()


@router.get("/by-apartment/{apt_id}")
def by_apartment(apt_id: str) -> list[Registration]:
    refresh_registration_statuses()
    return list_registrations_by_apartment(apt_id)


@router.get("/by-deal/{deal_id}")
def by_deal(deal_id: str) -> list[Registration]:
    refresh_registration_statuses()
    return list_registrations_by_deal(deal_id)


@router.get("/expiring")
def expiring_registrations() -> list[Registration]:
    refresh_registration_statuses()
    return [r for r in list_all_registrations() if r.status == RegistrationStatus.expiring_soon]


@router.post("/")
def create_registration(payload: RegistrationCreate) -> dict:
    reg = Registration(**payload.model_dump())
    created = add_registration(reg)

    apt = get_apartment(created.apartment_id)
    if apt and apt.current_reg_count >= 20:
        return {"registration": created, "warning": "approaching_limit"}
    return {"registration": created}


@router.get("/{reg_id}")
def get_registration_by_id(reg_id: str) -> Registration:
    reg = get_registration(reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="registration_not_found")
    return reg


@router.patch("/{reg_id}/close")
def close_registration(reg_id: str) -> Registration:
    reg = get_registration(reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="registration_not_found")
    reg.status = RegistrationStatus.closed
    return update_registration(reg)


@router.patch("/{reg_id}/mfc-doc")
def attach_mfc_doc(reg_id: str, payload: MfcDocUpdate) -> Registration:
    reg = get_registration(reg_id)
    if not reg:
        raise HTTPException(status_code=404, detail="registration_not_found")
    reg.mfc_doc_url = payload.mfc_doc_url
    return update_registration(reg)
