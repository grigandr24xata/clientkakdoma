from enum import Enum
import uuid

from pydantic import BaseModel, Field


class ApartmentStatus(str, Enum):
    free = "free"
    occupied = "occupied"
    partial = "partial"
    overloaded = "overloaded"
    soon_free = "soon_free"


class Apartment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    address: str
    rooms: int
    capacity_residents: int = 0
    monthly_reg_limit: int = 25
    current_reg_count: int = 0
    status: ApartmentStatus = ApartmentStatus.free
    owner_id: str | None = None
    active_deal_ids: list[str] = Field(default_factory=list)
    created_at: str = ""

    @property
    def reg_warning(self) -> bool:
        return self.current_reg_count >= 20

    @property
    def reg_limit_reached(self) -> bool:
        return self.current_reg_count >= self.monthly_reg_limit
