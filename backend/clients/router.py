from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.audit.service import log_action
from backend.clients.models import Client, ClientPassport
from backend.clients.store import add_passport_to_client, create_client, get_client, list_all_clients

router = APIRouter(prefix="/clients", tags=["clients"])


class ClientCreateRequest(BaseModel):
    phone: str = ""
    full_name_cyr: str = ""
    full_name_latin: str = ""
    date_of_birth: str = ""
    gender: str = ""
    citizenship: str = ""
    passports: list[ClientPassport] = Field(default_factory=list)


class PassportPatchRequest(BaseModel):
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


@router.get("/{client_id}", response_model=Client)
def get_client_by_id(client_id: str) -> Client:
    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("/", response_model=list[Client])
def get_clients() -> list[Client]:
    return list_all_clients()


@router.post("/", response_model=Client)
def create_client_manually(payload: ClientCreateRequest) -> Client:
    data = payload.model_dump()
    data["updated_at"] = datetime.utcnow()
    created = create_client(data)
    log_action(entity_type="client", entity_id=created.id, action="client_created", actor_id="system")
    return created


@router.patch("/{client_id}/passport", response_model=Client)
def patch_client_passport(client_id: str, payload: PassportPatchRequest) -> Client:
    client = get_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    passport = ClientPassport(**payload.model_dump())
    updated = add_passport_to_client(client_id, passport)
    log_action(entity_type="client", entity_id=updated.id, action="passport_added", actor_id="system")
    return updated
