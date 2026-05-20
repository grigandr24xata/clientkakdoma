from datetime import datetime

from backend.clients.models import Client, ClientPassport

_clients: dict[str, Client] = {}


def create_client(data: dict) -> Client:
    client = Client(**data)
    _clients[client.id] = client
    return client


def get_client(client_id: str) -> Client | None:
    return _clients.get(client_id)


def find_by_passport(series: str, number: str) -> Client | None:
    """Поиск по серии и номеру паспорта (exact match)."""
    for client in _clients.values():
        for passport in client.passports:
            if passport.series == series and passport.number == number:
                return client
    return None


def find_by_identity(full_name_cyr: str, date_of_birth: str) -> list[Client]:
    """Поиск по ФИО и дате рождения (probable match)."""
    results: list[Client] = []
    for client in _clients.values():
        if client.full_name_cyr == full_name_cyr and client.date_of_birth == date_of_birth:
            results.append(client)
    return results


def add_passport_to_client(client_id: str, passport: ClientPassport) -> Client:
    """Добавить новый паспорт в историю, пометить старый как не текущий."""
    client = _clients[client_id]
    for existing_passport in client.passports:
        existing_passport.is_current = False
    passport.is_current = True
    client.passports.append(passport)
    client.updated_at = datetime.utcnow()
    return client


def list_all_clients() -> list[Client]:
    return list(_clients.values())
