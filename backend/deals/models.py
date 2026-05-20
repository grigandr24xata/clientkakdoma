from datetime import date, datetime
from enum import Enum
import uuid

from pydantic import BaseModel, Field


class DealStatus(str, Enum):
    draft = "draft"
    client_data_collected = "client_data_collected"
    manager_review = "manager_review"
    docs_ready = "docs_ready"
    awaiting_sign = "awaiting_sign"
    awaiting_payment = "awaiting_payment"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"
    problem = "problem"


class DealBranch(str, Enum):
    apartment_registration = "apartment_registration"
    registration_only = "registration_only"


class DealResident(BaseModel):
    client_id: str
    is_main: bool = False


class Deal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    intake_case_id: str
    main_client_id: str
    branch: DealBranch
    status: DealStatus = DealStatus.draft
    residents: list[DealResident] = Field(default_factory=list)
    apartment_id: str | None = None
    manager_id: str | None = None
    date_start: date | None = None
    date_end: date | None = None
    rent_amount: float | None = None
    deposit: float | None = None
    commission: float | None = None
    registration_fee: float | None = None
    contract_url: str | None = None
    act_url: str | None = None
    video_url: str | None = None
    payment_confirmed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
