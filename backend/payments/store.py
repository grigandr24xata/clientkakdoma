from backend.payments.models import ClientPayment, OwnerPayment, OwnerPaymentStatus

_client_payments: dict[str, ClientPayment] = {}
_owner_payments: dict[str, OwnerPayment] = {}


def create_client_payment(p: ClientPayment) -> ClientPayment:
    _client_payments[p.id] = p
    return p


def get_client_payment(payment_id: str) -> ClientPayment | None:
    return _client_payments.get(payment_id)


def update_client_payment(p: ClientPayment) -> ClientPayment:
    _client_payments[p.id] = p
    return p


def list_client_payments_by_deal(deal_id: str) -> list[ClientPayment]:
    return [p for p in _client_payments.values() if p.deal_id == deal_id]


def create_owner_payment(p: OwnerPayment) -> OwnerPayment:
    _owner_payments[p.id] = p
    return p


def get_owner_payment(payment_id: str) -> OwnerPayment | None:
    return _owner_payments.get(payment_id)


def list_owner_payments_by_owner(owner_id: str) -> list[OwnerPayment]:
    return [p for p in _owner_payments.values() if p.owner_id == owner_id]


def list_upcoming_owner_payments(days_ahead: int = 3) -> list[OwnerPayment]:
    from datetime import date, timedelta

    today = date.today()
    cutoff = today + timedelta(days=days_ahead)
    return [
        p
        for p in _owner_payments.values()
        if p.status == OwnerPaymentStatus.planned and today <= p.planned_date <= cutoff
    ]


def list_overdue_owner_payments() -> list[OwnerPayment]:
    from datetime import date

    today = date.today()
    return [
        p
        for p in _owner_payments.values()
        if p.status == OwnerPaymentStatus.planned and p.planned_date < today
    ]


def update_owner_payment(p: OwnerPayment) -> OwnerPayment:
    _owner_payments[p.id] = p
    return p
