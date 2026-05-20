from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.deals.models import Deal, DealStatus
from backend.deals.service import try_activate_deal
from backend.deals.store import get_deal, list_deals, update_deal

router = APIRouter(prefix="/deals", tags=["deals"])


class ApartmentPatchRequest(BaseModel):
    apartment_id: str


class DatesPatchRequest(BaseModel):
    date_start: date
    date_end: date


class MoneyPatchRequest(BaseModel):
    rent_amount: float
    deposit: float
    commission: float
    registration_fee: float


class StatusPatchRequest(BaseModel):
    status: DealStatus


class DocumentsPatchRequest(BaseModel):
    contract_url: str | None = None
    act_url: str | None = None
    video_url: str | None = None


class PaymentPatchRequest(BaseModel):
    confirmed: bool


def _get_or_404(deal_id: str) -> Deal:
    deal = get_deal(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.get("/", response_model=list[Deal])
def get_deals() -> list[Deal]:
    return list_deals()


@router.get("/{deal_id}", response_model=Deal)
def get_deal_by_id(deal_id: str) -> Deal:
    return _get_or_404(deal_id)


@router.patch("/{deal_id}/apartment", response_model=Deal)
def patch_apartment(deal_id: str, payload: ApartmentPatchRequest) -> Deal:
    deal = _get_or_404(deal_id)
    deal.apartment_id = payload.apartment_id
    updated = update_deal(deal)
    return try_activate_deal(updated)


@router.patch("/{deal_id}/dates", response_model=Deal)
def patch_dates(deal_id: str, payload: DatesPatchRequest) -> Deal:
    deal = _get_or_404(deal_id)
    deal.date_start = payload.date_start
    deal.date_end = payload.date_end
    return update_deal(deal)


@router.patch("/{deal_id}/money", response_model=Deal)
def patch_money(deal_id: str, payload: MoneyPatchRequest) -> Deal:
    deal = _get_or_404(deal_id)
    deal.rent_amount = payload.rent_amount
    deal.deposit = payload.deposit
    deal.commission = payload.commission
    deal.registration_fee = payload.registration_fee
    return update_deal(deal)


@router.patch("/{deal_id}/status", response_model=Deal)
def patch_status(deal_id: str, payload: StatusPatchRequest) -> Deal:
    deal = _get_or_404(deal_id)
    if payload.status in {DealStatus.active, DealStatus.completed}:
        raise HTTPException(status_code=400, detail="Use activation conditions or complete endpoint")
    deal.status = payload.status
    return update_deal(deal)


@router.patch("/{deal_id}/documents", response_model=Deal)
def patch_documents(deal_id: str, payload: DocumentsPatchRequest) -> Deal:
    deal = _get_or_404(deal_id)
    deal.contract_url = payload.contract_url
    deal.act_url = payload.act_url
    deal.video_url = payload.video_url
    updated = update_deal(deal)
    return try_activate_deal(updated)


@router.patch("/{deal_id}/payment", response_model=Deal)
def patch_payment(deal_id: str, payload: PaymentPatchRequest) -> Deal:
    deal = _get_or_404(deal_id)
    deal.payment_confirmed = payload.confirmed
    updated = update_deal(deal)
    return try_activate_deal(updated)


@router.post("/{deal_id}/complete", response_model=Deal)
def complete_deal(deal_id: str) -> Deal:
    deal = _get_or_404(deal_id)
    deal.status = DealStatus.completed
    return update_deal(deal)
