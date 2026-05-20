from datetime import date, datetime
from enum import Enum
import uuid

from pydantic import BaseModel, Field


class PaymentType(str, Enum):
    rent = "rent"
    deposit = "deposit"
    commission = "commission"
    registration = "registration"


class PaymentMethod(str, Enum):
    cash = "cash"
    transfer = "transfer"


class ClientPayment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    deal_id: str
    type: PaymentType
    amount: float
    currency: str = "RUB"
    paid_at: datetime | None = None
    confirmed_by: str | None = None
    payment_method: PaymentMethod = PaymentMethod.cash
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OwnerPaymentStatus(str, Enum):
    planned = "planned"
    paid = "paid"
    overdue = "overdue"


class OwnerPayment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    owner_id: str
    apartment_id: str
    amount: float
    currency: str = "RUB"
    planned_date: date
    paid_at: datetime | None = None
    status: OwnerPaymentStatus = OwnerPaymentStatus.planned
    created_at: datetime = Field(default_factory=datetime.utcnow)
