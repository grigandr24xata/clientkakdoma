from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class ClientPassport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    series: str = ""
    number: str = ""
    issued_by: str = ""
    issued_date: str = ""
    expiry_date: str = ""
    birth_place: str = ""
    mrz_raw: str = ""
    passport_hash: str = ""
    is_current: bool = True
    ocr_confidence: float = 0.0
    auto_accepted: bool = False
    manual_check: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class Client(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phone: str = ""
    full_name_cyr: str = ""
    full_name_latin: str = ""
    date_of_birth: str = ""
    gender: str = ""
    citizenship: str = ""
    passports: list[ClientPassport] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow())
