from backend.clients.models import Client
from backend.clients.store import find_by_identity, find_by_passport


class DedupResult:
    def __init__(self, match_type: str, client: Client | None = None, manual_check: bool = False, reason: str = ""):
        self.match_type = match_type
        self.client = client
        self.manual_check = manual_check
        self.reason = reason


def dedup_resident(ocr_data: dict) -> DedupResult:
    """
    Проверить OCR данные жильца против базы клиентов.
    ocr_data содержит: series, number, full_name_cyr, date_of_birth, passport_hash
    """
    series = ocr_data.get("fields", {}).get("series", "") or ocr_data.get("series", "")
    number = ocr_data.get("fields", {}).get("passport_number", "") or ocr_data.get("number", "")
    full_name = ocr_data.get("fields", {}).get("full_name_cyr", "") or ocr_data.get("full_name_cyr", "")
    dob = ocr_data.get("fields", {}).get("date_of_birth", "") or ocr_data.get("date_of_birth", "")

    if series and number:
        existing = find_by_passport(series, number)
        if existing:
            return DedupResult("exact_match", client=existing)

    if full_name and dob:
        candidates = find_by_identity(full_name, dob)
        if len(candidates) == 1:
            return DedupResult(
                "probable_match",
                client=candidates[0],
                manual_check=True,
                reason="Same identity, different passport — manager review required",
            )
        if len(candidates) > 1:
            return DedupResult(
                "manual_review_required",
                manual_check=True,
                reason="Multiple clients with same identity found",
            )

    return DedupResult("no_match")


def dedup_within_intake(residents_ocr_data: list[dict]) -> list[str]:
    """
    Проверить дубли внутри одной заявки.
    Возвращает список passport_hash которые встречаются больше одного раза.
    """
    hashes = []
    for ocr in residents_ocr_data:
        passport_hash = ocr.get("fields", {}).get("passport_hash") or ocr.get("passport_hash", "")
        if passport_hash:
            hashes.append(passport_hash)

    seen = set()
    duplicates = []
    for passport_hash in hashes:
        if passport_hash in seen:
            duplicates.append(passport_hash)
        seen.add(passport_hash)
    return duplicates
