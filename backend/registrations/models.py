from datetime import date, datetime
from enum import Enum
import uuid

from pydantic import BaseModel, Field


class RegistrationStatus(str, Enum):
    planned = "planned"
    active = "active"
    expiring_soon = "expiring_soon"
    expired = "expired"
    closed = "closed"


class Registration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    deal_id: str
    client_id: str
    apartment_id: str
    date_start: date
    date_end: date
    status: RegistrationStatus = RegistrationStatus.planned
    mfc_doc_url: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
