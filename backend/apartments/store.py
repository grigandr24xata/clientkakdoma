from backend.apartments.models import Apartment, ApartmentStatus

_apartments: dict[str, Apartment] = {}


def create_apartment(data: dict) -> Apartment:
    ap = Apartment(**data)
    if ap.capacity_residents == 0:
        ap.capacity_residents = ap.rooms * 3
    _apartments[ap.id] = ap
    return ap


def get_apartment(apt_id: str) -> Apartment | None:
    return _apartments.get(apt_id)


def list_apartments() -> list[Apartment]:
    return list(_apartments.values())


def update_apartment(apt: Apartment) -> Apartment:
    _apartments[apt.id] = apt
    return apt


def get_free_apartments() -> list[Apartment]:
    return [a for a in _apartments.values() if a.status in (ApartmentStatus.free, ApartmentStatus.partial)]
