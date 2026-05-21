from collections import defaultdict

from backend.apartments.models import ApartmentStatus
from backend.apartments.store import list_apartments
from backend.clients.store import list_all_clients
from backend.deals.models import DealStatus
from backend.deals.store import list_deals
from backend.payments.store import list_overdue_owner_payments, list_upcoming_owner_payments
from backend.registrations.models import RegistrationStatus
from backend.registrations.service import refresh_registration_statuses
from backend.registrations.store import list_all_registrations


def get_deals_summary() -> dict:
    deals = list_deals()
    by_status = defaultdict(int)
    for d in deals:
        by_status[d.status.value] += 1
    return {
        "total": len(deals),
        "by_status": dict(by_status),
        "new": by_status[DealStatus.draft.value] + by_status[DealStatus.client_data_collected.value],
        "pending_review": by_status[DealStatus.manager_review.value],
        "awaiting_sign": by_status[DealStatus.awaiting_sign.value],
        "awaiting_payment": by_status[DealStatus.awaiting_payment.value],
        "active": by_status[DealStatus.active.value],
        "problem": by_status[DealStatus.problem.value],
        "completed": by_status[DealStatus.completed.value],
    }


def get_registrations_summary() -> dict:
    refresh_registration_statuses()
    regs = list_all_registrations()
    by_status = defaultdict(int)
    by_apartment = defaultdict(int)
    for r in regs:
        by_status[r.status.value] += 1
        by_apartment[r.apartment_id] += 1
    return {
        "total": len(regs),
        "by_status": dict(by_status),
        "active": by_status[RegistrationStatus.active.value],
        "expiring_soon": by_status[RegistrationStatus.expiring_soon.value],
        "expired": by_status[RegistrationStatus.expired.value],
        "by_apartment": dict(by_apartment),
    }


def get_apartments_summary() -> dict:
    apts = list_apartments()
    by_status = defaultdict(int)
    warnings = []
    for a in apts:
        by_status[a.status.value] += 1
        if a.reg_warning:
            warnings.append(
                {
                    "apartment_id": a.id,
                    "address": a.address,
                    "current_reg_count": a.current_reg_count,
                    "monthly_reg_limit": a.monthly_reg_limit,
                }
            )
    return {
        "total": len(apts),
        "by_status": dict(by_status),
        "free": by_status[ApartmentStatus.free.value],
        "occupied": by_status[ApartmentStatus.occupied.value],
        "partial": by_status[ApartmentStatus.partial.value],
        "overloaded": by_status[ApartmentStatus.overloaded.value],
        "reg_limit_warnings": warnings,
    }


def get_finance_summary() -> dict:
    from backend.payments.store import _client_payments

    payments = list(_client_payments.values())
    by_type = defaultdict(float)
    by_month = defaultdict(float)
    total = 0.0
    for p in payments:
        if p.paid_at:
            by_type[p.type.value] += p.amount
            month_key = p.paid_at.strftime("%Y-%m") if hasattr(p.paid_at, "strftime") else str(p.paid_at)[:7]
            by_month[month_key] += p.amount
            total += p.amount
    return {
        "total_revenue": round(total, 2),
        "by_type": {k: round(v, 2) for k, v in by_type.items()},
        "by_month": {k: round(v, 2) for k, v in sorted(by_month.items())},
    }


def get_owner_payments_summary() -> dict:
    upcoming = list_upcoming_owner_payments(days_ahead=3)
    overdue = list_overdue_owner_payments()
    return {
        "upcoming_count": len(upcoming),
        "overdue_count": len(overdue),
        "upcoming": [
            {
                "id": p.id,
                "owner_id": p.owner_id,
                "apartment_id": p.apartment_id,
                "amount": p.amount,
                "planned_date": str(p.planned_date),
            }
            for p in upcoming
        ],
        "overdue": [
            {
                "id": p.id,
                "owner_id": p.owner_id,
                "apartment_id": p.apartment_id,
                "amount": p.amount,
                "planned_date": str(p.planned_date),
            }
            for p in overdue
        ],
    }


def get_management_summary() -> dict:
    deals_s = get_deals_summary()
    finance_s = get_finance_summary()
    regs_s = get_registrations_summary()
    apts_s = get_apartments_summary()
    owners_s = get_owner_payments_summary()
    clients_total = len(list_all_clients())
    return {
        "clients_total": clients_total,
        "deals": deals_s,
        "registrations": regs_s,
        "apartments": apts_s,
        "finance": finance_s,
        "owner_payments": owners_s,
    }
