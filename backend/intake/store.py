from datetime import datetime, timezone
import uuid

from backend.intake.models import IntakeBranch, IntakeCase

_cases: dict[str, IntakeCase] = {}


def create_case(phone: str) -> IntakeCase:
    case_id = str(uuid.uuid4())
    now = datetime.now(tz=timezone.utc)
    case = IntakeCase(
        id=case_id,
        phone=phone,
        branch=IntakeBranch.apartment_registration,
        step="phone_verified",
        status="draft",
        residents=[],
        resident_count=0,
        created_at=now,
        updated_at=now,
    )
    _cases[case_id] = case
    return case


def get_case(case_id: str) -> IntakeCase | None:
    return _cases.get(case_id)


def find_draft_by_phone(phone: str) -> str | None:
    for case in _cases.values():
        if case.phone == phone and case.status == "draft":
            return case.id
    return None


def update_case(case: IntakeCase) -> IntakeCase:
    case.updated_at = datetime.now(tz=timezone.utc)
    _cases[case.id] = case
    return case


def list_cases_by_phone(phone: str) -> list[IntakeCase]:
    return [case for case in _cases.values() if case.phone == phone]
