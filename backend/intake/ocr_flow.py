import uuid

from backend.files.store import FileRecord, save_file_record
from backend.ocr.metrics import record_ocr_metric
from backend.ocr.service import process_passport_ocr


async def handle_passport_upload(
    *,
    intake_case_id: str,
    resident_order_index: int,
    image_bytes: bytes,
    content_type: str,
    original_filename: str,
    correlation_id: str | None = None,
) -> dict:
    """
    1. Сохранить файл паспорта в store (заглушка S3)
    2. Запустить OCR через canonical pipeline
    3. Записать метрику с привязкой к жильцу
    4. Вернуть OCR результат для подтверждения клиентом
    НЕ сохраняет ocr_data в resident — клиент подтверждает через PATCH /ocr
    """
    corr = correlation_id or str(uuid.uuid4())

    file_key = f"intake/{intake_case_id}/resident_{resident_order_index}/passport_{corr}"
    file_record = FileRecord(
        intake_case_id=intake_case_id,
        resident_order_index=resident_order_index,
        file_type="passport",
        original_filename=original_filename,
        content_type=content_type,
        size_bytes=len(image_bytes),
        storage_key=file_key,
        storage_url=f"stub://{file_key}",
    )
    save_file_record(file_record)

    ocr_result = await process_passport_ocr(image_bytes, corr)

    record_ocr_metric(
        correlation_id=corr,
        ocr_result=ocr_result,
        intake_resident_id=f"{intake_case_id}:{resident_order_index}",
    )

    return {
        "file_id": file_record.id,
        "correlation_id": corr,
        "ocr_result": ocr_result,
        "needs_manual_review": ocr_result.get("manual_check", False),
    }
