from datetime import date, timedelta

from backend.apartments.store import get_apartment, update_apartment
from backend.registrations.models import Registration, RegistrationStatus
from backend.registrations.store import list_all_registrations, update_registration


def refresh_registration_statuses() -> int:
    """
    Пересчитать статусы всех регистраций.
    Вызывать периодически (или при каждом GET /registrations/).
    Возвращает количество обновлённых записей.
    """
    today = date.today()
    updated = 0
    for reg in list_all_registrations():
        if reg.status in (RegistrationStatus.closed, RegistrationStatus.expired):
            continue

        new_status = reg.status
        if reg.date_end < today:
            new_status = RegistrationStatus.expired
        elif reg.date_end - today <= timedelta(days=7):
            new_status = RegistrationStatus.expiring_soon
        elif reg.date_start <= today:
            new_status = RegistrationStatus.active

        if new_status != reg.status:
            reg.status = new_status
            update_registration(reg)
            updated += 1
    return updated


def add_registration(reg: Registration) -> Registration:
    """Создать регистрацию и увеличить счётчик квартиры."""
    from backend.registrations.store import create_registration

    created = create_registration(reg)
    apt = get_apartment(reg.apartment_id)
    if apt:
        apt.current_reg_count += 1
        update_apartment(apt)
    return created
