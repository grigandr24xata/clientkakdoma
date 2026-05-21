from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class FileRecord:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intake_case_id: str = ""
    resident_order_index: int | None = None
    file_type: str = ""  # passport | migration_card | patent | work_contract | other
    original_filename: str = ""
    content_type: str = ""
    size_bytes: int = 0
    storage_key: str = ""
    storage_url: str = ""  # в prod — реальный S3 URL
    uploaded_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


_files: list[FileRecord] = []


def save_file_record(record: FileRecord) -> FileRecord:
    _files.append(record)
    return record


def get_files_for_case(intake_case_id: str) -> list[FileRecord]:
    return [f for f in _files if f.intake_case_id == intake_case_id]


def get_files_for_resident(intake_case_id: str, order_index: int) -> list[FileRecord]:
    return [f for f in _files if f.intake_case_id == intake_case_id and f.resident_order_index == order_index]


def save_file_bytes(
    *,
    intake_case_id: str,
    resident_order_index: int | None,
    file_type: str,
    original_filename: str,
    content_type: str,
    data: bytes,
) -> FileRecord:
    from backend.config import settings

    key = f"intake/{intake_case_id}/{file_type}/{original_filename}"
    if settings.USE_DATABASE:
        from backend.files.s3 import upload_file

        url = upload_file(key, data, content_type)
    else:
        url = f"stub://{key}"
    record = FileRecord(
        intake_case_id=intake_case_id,
        resident_order_index=resident_order_index,
        file_type=file_type,
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=len(data),
        storage_key=key,
        storage_url=url,
    )
    return save_file_record(record)
