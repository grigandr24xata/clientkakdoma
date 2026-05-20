from datetime import datetime
from enum import Enum
import uuid

from pydantic import BaseModel, Field


class IntakeBranch(str, Enum):
    apartment_registration = "apartment_registration"
    registration_only = "registration_only"


class IntakeResident(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_index: int
    full_name: str | None = None
    is_main: bool = False
    phone: str | None = None
    ocr_data: dict | None = None
    ocr_confirmed: bool = False
    extra_docs_uploaded: bool = False


class IntakeCase(BaseModel):
    id: str
    phone: str
    branch: IntakeBranch
    resident_count: int = 0
    step: str = "phone_verified"
    status: str = "draft"
    residents: list[IntakeResident] = Field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
