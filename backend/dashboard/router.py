from fastapi import APIRouter

from backend.audit.service import get_recent_actions, serialize_entries
from backend.dashboard.service import (
    get_apartments_summary,
    get_deals_summary,
    get_finance_summary,
    get_management_summary,
    get_owner_payments_summary,
    get_registrations_summary,
)
from backend.ocr.metrics import get_ocr_quality_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
def get_dashboard_management_summary() -> dict:
    return get_management_summary()


@router.get("/deals")
def get_dashboard_deals_summary() -> dict:
    return get_deals_summary()


@router.get("/registrations")
def get_dashboard_registrations_summary() -> dict:
    return get_registrations_summary()


@router.get("/apartments")
def get_dashboard_apartments_summary() -> dict:
    return get_apartments_summary()


@router.get("/finance")
def get_dashboard_finance_summary() -> dict:
    return get_finance_summary()


@router.get("/owner-payments")
def get_dashboard_owner_payments_summary() -> dict:
    return get_owner_payments_summary()


@router.get("/ocr-quality")
def get_dashboard_ocr_quality() -> dict:
    return get_ocr_quality_dashboard()


@router.get("/recent-activity")
def get_dashboard_recent_activity() -> list[dict]:
    return serialize_entries(get_recent_actions(limit=10))
