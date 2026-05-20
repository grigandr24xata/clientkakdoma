from backend.apartments.models import Apartment, ApartmentStatus


def recalculate_apartment_status(apt: Apartment, active_deals_count: int, total_residents: int) -> Apartment:
    """Пересчитать статус квартиры на основе текущей загрузки."""
    if apt.reg_limit_reached:
        apt.status = ApartmentStatus.overloaded
    elif total_residents == 0:
        apt.status = ApartmentStatus.free
    elif total_residents < apt.capacity_residents:
        apt.status = ApartmentStatus.partial
    else:
        apt.status = ApartmentStatus.occupied
    return apt
