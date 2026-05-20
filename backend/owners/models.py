from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class Owner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    phone: str = ""
    payment_day: int = 1
    apartment_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
