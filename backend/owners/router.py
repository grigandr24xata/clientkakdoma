from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.apartments.store import list_apartments
from backend.owners.models import Owner
from backend.owners.store import create_owner, get_owner, list_owners, update_owner

router = APIRouter(prefix="/owners", tags=["owners"])


class OwnerCreateRequest(BaseModel):
    full_name: str
    phone: str = ""
    payment_day: int = 1


class OwnerPatchRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    payment_day: int | None = None


@router.get("/", response_model=list[Owner])
def get_owners() -> list[Owner]:
    return list_owners()


@router.get("/{owner_id}", response_model=Owner)
def get_owner_by_id(owner_id: str) -> Owner:
    owner = get_owner(owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    return owner


@router.post("/", response_model=Owner)
def create_new_owner(payload: OwnerCreateRequest) -> Owner:
    return create_owner(payload.model_dump())


@router.patch("/{owner_id}", response_model=Owner)
def patch_owner(owner_id: str, payload: OwnerPatchRequest) -> Owner:
    owner = get_owner(owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    if payload.full_name is not None:
        owner.full_name = payload.full_name
    if payload.phone is not None:
        owner.phone = payload.phone
    if payload.payment_day is not None:
        owner.payment_day = payload.payment_day

    return update_owner(owner)


@router.get("/{owner_id}/apartments")
def get_owner_apartments(owner_id: str) -> list:
    owner = get_owner(owner_id)
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    return [apt for apt in list_apartments() if apt.owner_id == owner_id]
