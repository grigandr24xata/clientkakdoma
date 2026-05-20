from datetime import date, datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.deals.service import try_activate_deal
from backend.deals.store import get_deal, update_deal
from backend.payments.models import (
    ClientPayment,
    OwnerPayment,
    OwnerPaymentStatus,
    PaymentMethod,
    PaymentType,
)
from backend.payments.store import (
    create_client_payment,
    create_owner_payment,
    get_client_payment,
    get_owner_payment,
    list_client_payments_by_deal,
    list_overdue_owner_payments,
    list_owner_payments_by_owner,
    list_upcoming_owner_payments,
    update_client_payment,
    update_owner_payment,
)

router = APIRouter(prefix="/payments", tags=["payments"])


class ClientPaymentCreate(BaseModel):
    deal_id: str
    type: PaymentType
    amount: float
    payment_method: PaymentMethod = PaymentMethod.cash


class ClientPaymentConfirm(BaseModel):
    confirmed_by: str


class OwnerPaymentCreate(BaseModel):
    owner_id: str
    apartment_id: str
    amount: float
    planned_date: date


class OwnerPaymentPay(BaseModel):
    paid_at: datetime | None = None


@router.post("/client")
def create_client(p: ClientPaymentCreate) -> ClientPayment:
    payment = ClientPayment(**p.model_dump())
    return create_client_payment(payment)


@router.get("/client/by-deal/{deal_id}")
def client_by_deal(deal_id: str) -> list[ClientPayment]:
    return list_client_payments_by_deal(deal_id)


@router.patch("/client/{payment_id}/confirm")
def confirm_client(payment_id: str, payload: ClientPaymentConfirm) -> ClientPayment:
    payment = get_client_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="payment_not_found")

    payment.confirmed_by = payload.confirmed_by
    payment.paid_at = payment.paid_at or datetime.utcnow()
    update_client_payment(payment)

    deal = get_deal(payment.deal_id)
    if deal:
        deal.payment_confirmed = True
        updated_deal = update_deal(deal)
        try_activate_deal(updated_deal)

    return payment


@router.post("/owner")
def create_owner(p: OwnerPaymentCreate) -> OwnerPayment:
    payment = OwnerPayment(**p.model_dump())
    return create_owner_payment(payment)


@router.get("/owner/by-owner/{owner_id}")
def owner_by_owner(owner_id: str) -> list[OwnerPayment]:
    return list_owner_payments_by_owner(owner_id)


@router.get("/owner/upcoming")
def upcoming_owner() -> list[OwnerPayment]:
    return list_upcoming_owner_payments(days_ahead=3)


@router.get("/owner/overdue")
def overdue_owner() -> list[OwnerPayment]:
    return list_overdue_owner_payments()


@router.patch("/owner/{payment_id}/pay")
def mark_owner_paid(payment_id: str, payload: OwnerPaymentPay) -> OwnerPayment:
    payment = get_owner_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="payment_not_found")

    payment.paid_at = payload.paid_at or datetime.utcnow()
    payment.status = OwnerPaymentStatus.paid
    return update_owner_payment(payment)
