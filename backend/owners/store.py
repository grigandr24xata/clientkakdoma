from backend.owners.models import Owner

_owners: dict[str, Owner] = {}


def create_owner(data: dict) -> Owner:
    owner = Owner(**data)
    _owners[owner.id] = owner
    return owner


def get_owner(owner_id: str) -> Owner | None:
    return _owners.get(owner_id)


def list_owners() -> list[Owner]:
    return list(_owners.values())


def update_owner(owner: Owner) -> Owner:
    _owners[owner.id] = owner
    return owner
