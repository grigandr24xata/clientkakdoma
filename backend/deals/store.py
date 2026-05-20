from datetime import datetime

from backend.deals.models import Deal

_deals: dict[str, Deal] = {}


def create_deal(deal: Deal) -> Deal:
    _deals[deal.id] = deal
    return deal


def get_deal(deal_id: str) -> Deal | None:
    return _deals.get(deal_id)


def get_deal_by_intake(intake_case_id: str) -> Deal | None:
    for d in _deals.values():
        if d.intake_case_id == intake_case_id:
            return d
    return None


def update_deal(deal: Deal) -> Deal:
    deal.updated_at = datetime.utcnow()
    _deals[deal.id] = deal
    return deal


def list_deals() -> list[Deal]:
    return list(_deals.values())
