from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.apartments.models import Apartment
from backend.apartments.service import recalculate_apartment_status
from backend.apartments.store import create_apartment, get_apartment, get_free_apartments, list_apartments, update_apartment

router = APIRouter(prefix="/apartments", tags=["apartments"])


class ApartmentCreateRequest(BaseModel):
    address: str
    rooms: int
    owner_id: str | None = None


class ApartmentPatchRequest(BaseModel):
    address: str | None = None
    rooms: int | None = None
    owner_id: str | None = None


@router.get("/", response_model=list[Apartment])
def get_apartments() -> list[Apartment]:
    return list_apartments()


@router.get("/free", response_model=list[Apartment])
def get_available_apartments() -> list[Apartment]:
    return get_free_apartments()


@router.get("/{apt_id}", response_model=Apartment)
def get_apartment_by_id(apt_id: str) -> Apartment:
    apt = get_apartment(apt_id)
    if not apt:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apt


@router.post("/", response_model=Apartment)
def create_new_apartment(payload: ApartmentCreateRequest) -> Apartment:
    data = payload.model_dump()
    data["capacity_residents"] = payload.rooms * 3
    return create_apartment(data)


@router.patch("/{apt_id}", response_model=Apartment)
def patch_apartment(apt_id: str, payload: ApartmentPatchRequest) -> Apartment:
    apt = get_apartment(apt_id)
    if not apt:
        raise HTTPException(status_code=404, detail="Apartment not found")

    if payload.address is not None:
        apt.address = payload.address
    if payload.rooms is not None:
        apt.rooms = payload.rooms
        apt.capacity_residents = payload.rooms * 3
    if payload.owner_id is not None:
        apt.owner_id = payload.owner_id

    updated = recalculate_apartment_status(apt, active_deals_count=len(apt.active_deal_ids), total_residents=0)
    return update_apartment(updated)


@router.get("/{apt_id}/status")
def get_apartment_status(apt_id: str) -> dict[str, str | int | bool]:
    apt = get_apartment(apt_id)
    if not apt:
        raise HTTPException(status_code=404, detail="Apartment not found")

    return {
        "status": apt.status,
        "reg_count": apt.current_reg_count,
        "reg_warning": apt.reg_warning,
        "reg_limit_reached": apt.reg_limit_reached,
        "capacity": apt.capacity_residents,
    }
