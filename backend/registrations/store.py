from datetime import datetime

from backend.registrations.models import Registration

_registrations: dict[str, Registration] = {}


def create_registration(reg: Registration) -> Registration:
    _registrations[reg.id] = reg
    return reg


def get_registration(reg_id: str) -> Registration | None:
    return _registrations.get(reg_id)


def list_registrations_by_deal(deal_id: str) -> list[Registration]:
    return [r for r in _registrations.values() if r.deal_id == deal_id]


def list_registrations_by_apartment(apartment_id: str) -> list[Registration]:
    return [r for r in _registrations.values() if r.apartment_id == apartment_id]


def update_registration(reg: Registration) -> Registration:
    reg.updated_at = datetime.utcnow()
    _registrations[reg.id] = reg
    return reg


def list_all_registrations() -> list[Registration]:
    return list(_registrations.values())
