import io
import logging

from aiogram import Bot, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from adapters.telegram.backend_client import BackendClient
from adapters.telegram.keyboards import (
    branch_keyboard,
    extra_docs_keyboard,
    final_confirm_keyboard,
    ocr_confirm_keyboard,
    resident_count_keyboard,
)
from adapters.telegram.states import AuthFlow, IntakeFlow

logger = logging.getLogger(__name__)


# ─── AUTH FLOW ────────────────────────────────────────────────────────────────


async def cmd_start(message: Message, state: FSMContext, backend: BackendClient):
    """Старт: очистить state, спросить телефон."""
    await state.clear()
    # Проверить нет ли уже активной сессии
    data = await state.get_data()
    if data.get("access_token"):
        await message.answer(
            "У вас есть активная сессия. Продолжаем с того места где остановились."
        )
        await resume_intake(message, state, backend)
        return
    await state.set_state(AuthFlow.waiting_phone)
    await message.answer(
        "Добро пожаловать!\n\n"
        "Введите ваш номер телефона в формате +7XXXXXXXXXX:"
    )


async def handle_phone_input(message: Message, state: FSMContext, backend: BackendClient):
    """Принять телефон, вызвать /auth/phone/start."""
    phone = (message.text or "").strip()
    import re

    if not re.fullmatch(r"(\+7|8)\d{10}", phone):
        await message.answer("Неверный формат. Введите телефон: +7XXXXXXXXXX")
        return
    if phone.startswith("8"):
        phone = "+7" + phone[1:]
    try:
        result = await backend.phone_start(phone)
        await state.update_data(phone=phone)
        await state.set_state(AuthFlow.waiting_code)
        # В dev режиме backend возвращает dev_code
        if result.get("dev_code"):
            await message.answer(
                f"Код подтверждения (DEV): {result['dev_code']}\n" "Введите код:"
            )
        else:
            await message.answer("Код отправлен на ваш номер. Введите код:")
    except Exception as e:
        logger.error("phone_start failed: %s", e)
        await message.answer("Ошибка отправки кода. Попробуйте позже.")


async def handle_code_input(message: Message, state: FSMContext, backend: BackendClient):
    """Принять код, вызвать /auth/phone/verify, получить JWT."""
    code = (message.text or "").strip()
    data = await state.get_data()
    phone = data.get("phone", "")
    try:
        result = await backend.phone_verify(phone, code)
        token = result["access_token"]
        draft_id = result.get("draft_intake_case_id")
        await state.update_data(access_token=token, phone=phone)
        if draft_id:
            await state.update_data(case_id=draft_id)
            await message.answer(
                "✅ Вы вошли в систему.\n\n"
                "Найден незавершённый черновик. Продолжаем с того места."
            )
            await resume_intake(message, state, backend)
        else:
            await start_intake(message, state)
    except Exception as e:
        logger.error("phone_verify failed: %s", e)
        await message.answer("Неверный код или истёк срок действия. Попробуйте ещё раз.")


# ─── INTAKE FLOW ─────────────────────────────────────────────────────────────


async def start_intake(message: Message, state: FSMContext):
    """Начать новый intake — выбор ветки."""
    await state.set_state(IntakeFlow.waiting_branch)
    await message.answer("Выберите тип услуги:", reply_markup=branch_keyboard())


async def resume_intake(message: Message, state: FSMContext, backend: BackendClient):
    """Восстановить intake из черновика — определить текущий шаг."""
    data = await state.get_data()
    token = data.get("access_token", "")
    case_id = data.get("case_id", "")
    try:
        case = await backend.get_intake_case(token, case_id)
        step = case.get("step", "")
        resident_count = case.get("resident_count", 0)
        # Определить с какого шага продолжить
        if step in ("branch_selected", "phone_verified"):
            await state.set_state(IntakeFlow.waiting_resident_count)
            await message.answer(
                "Сколько жильцов будет проживать?", reply_markup=resident_count_keyboard()
            )
        elif step == "residents_count_set" or step.startswith("passport_upload"):
            # Найти первого неподтверждённого жильца
            residents = case.get("residents", [])
            next_idx = next(
                (r["order_index"] for r in residents if not r.get("ocr_confirmed")), None
            )
            if next_idx:
                await state.update_data(current_resident_index=next_idx)
                await state.set_state(IntakeFlow.waiting_passport_photo)
                await message.answer(
                    f"Продолжаем. Жилец {next_idx} из {resident_count}.\n"
                    "Отправьте фото паспорта (разворот с фото):"
                )
            else:
                await state.set_state(IntakeFlow.waiting_extra_docs)
                await message.answer(
                    "Все паспорта обработаны.\n"
                    "Загрузите дополнительные документы или нажмите Готово:",
                    reply_markup=extra_docs_keyboard(),
                )
        elif step == "extra_docs":
            await state.set_state(IntakeFlow.waiting_extra_docs)
            await message.answer(
                "Загрузите дополнительные документы или нажмите Готово:",
                reply_markup=extra_docs_keyboard(),
            )
        else:
            await start_intake(message, state)
    except Exception:
        await start_intake(message, state)


async def handle_branch_select(
    callback: CallbackQuery, state: FSMContext, backend: BackendClient
):
    """Выбор ветки → создать intake case."""
    await callback.answer()
    branch = (callback.data or "").replace("branch_", "", 1)
    data = await state.get_data()
    token = data.get("access_token", "")
    try:
        case = await backend.create_intake_case(token, branch)
        await state.update_data(case_id=case["id"], branch=branch)
        await state.set_state(IntakeFlow.waiting_resident_count)
        await callback.message.answer(
            "Сколько жильцов будет проживать?", reply_markup=resident_count_keyboard()
        )
    except Exception as e:
        logger.error("create_intake_case failed: %s", e)
        await callback.message.answer("Ошибка создания заявки. Попробуйте ещё раз.")


async def handle_resident_count(
    callback: CallbackQuery, state: FSMContext, backend: BackendClient
):
    """Выбор количества жильцов."""
    await callback.answer()
    count = int((callback.data or "").replace("count_", "", 1))
    data = await state.get_data()
    token = data.get("access_token", "")
    case_id = data.get("case_id", "")
    try:
        await backend.set_resident_count(token, case_id, count)
        await state.update_data(resident_count=count, current_resident_index=1)
        await state.set_state(IntakeFlow.waiting_passport_photo)
        await callback.message.answer(
            f"Жилец 1 из {count}.\n"
            "Отправьте фото паспорта (разворот с фото и данными):"
        )
    except Exception as e:
        logger.error("set_resident_count failed: %s", e)
        await callback.message.answer("Ошибка. Попробуйте ещё раз.")


async def handle_passport_photo(
    message: Message, bot: Bot, state: FSMContext, backend: BackendClient
):
    """Загрузить паспорт → OCR → показать результат для подтверждения."""
    data = await state.get_data()
    token = data.get("access_token", "")
    case_id = data.get("case_id", "")
    order_index = int(data.get("current_resident_index", 1))
    resident_count = int(data.get("resident_count", 1))

    photo = message.photo[-1]
    try:
        file = await bot.get_file(photo.file_id)
        buf = io.BytesIO()
        await bot.download(file, destination=buf)
        image_bytes = buf.getvalue()
    except Exception as e:
        logger.error("photo download failed: %s", e)
        await message.answer("Не удалось обработать фото. Попробуйте ещё раз.")
        return

    await message.answer("⏳ Обрабатываю паспорт...")

    try:
        result = await backend.upload_passport(token, case_id, order_index, image_bytes)
        ocr = result.get("ocr_result", {})
        fields = ocr.get("fields", {})
        needs_review = result.get("needs_manual_review", False)

        # Сохранить OCR результат в state для подтверждения
        await state.update_data(
            last_ocr_result=ocr,
            last_order_index=order_index,
        )

        preview = (
            f"Жилец {order_index} из {resident_count}\n\n"
            f"Фамилия: {fields.get('surname', '—')}\n"
            f"Имя: {fields.get('given_names', '—')}\n"
            f"Дата рождения: {fields.get('date_of_birth', '—')}\n"
            f"Гражданство: {fields.get('nationality', '—')}\n"
            f"Паспорт: ***{str(fields.get('passport_number', ''))[-4:]}"
        )
        if needs_review:
            preview += "\n\n⚠️ Низкое качество распознавания. Проверьте данные."

        await state.set_state(IntakeFlow.waiting_ocr_confirm)
        await message.answer(preview, reply_markup=ocr_confirm_keyboard(needs_review))
    except Exception as e:
        logger.error("upload_passport failed: %s", e)
        await message.answer("Ошибка обработки. Попробуйте ещё раз или переснимите.")


async def handle_ocr_confirm(
    callback: CallbackQuery, state: FSMContext, backend: BackendClient
):
    """Подтверждение OCR данных."""
    await callback.answer()
    action = callback.data or ""
    data = await state.get_data()
    token = data.get("access_token", "")
    case_id = data.get("case_id", "")
    order_index = int(data.get("last_order_index", 1))
    ocr_result = data.get("last_ocr_result", {})
    resident_count = int(data.get("resident_count", 1))

    if action == "ocr_retake":
        await state.set_state(IntakeFlow.waiting_passport_photo)
        await callback.message.answer(
            f"Жилец {order_index} из {resident_count}.\n" "Отправьте новое фото паспорта:"
        )
        return

    confirmed = action in ("ocr_confirm", "ocr_confirm_manual")
    try:
        await backend.confirm_ocr(token, case_id, order_index, ocr_result, confirmed)
        next_index = order_index + 1
        if next_index <= resident_count:
            await state.update_data(current_resident_index=next_index)
            await state.set_state(IntakeFlow.waiting_passport_photo)
            await callback.message.answer(
                f"Жилец {next_index} из {resident_count}.\n" "Отправьте фото паспорта:"
            )
        else:
            await state.set_state(IntakeFlow.waiting_extra_docs)
            await callback.message.answer(
                "✅ Все паспорта обработаны.\n\n"
                "Загрузите дополнительные документы (миграционная карта, патент и др.)\n"
                "или нажмите Готово если документов нет:",
                reply_markup=extra_docs_keyboard(),
            )
    except Exception as e:
        logger.error("confirm_ocr failed: %s", e)
        await callback.message.answer("Ошибка. Попробуйте ещё раз.")


async def handle_extra_doc_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа доп.документа — запросить файл."""
    await callback.answer()
    doc_type = (callback.data or "").replace("doc_", "", 1)
    type_names = {
        "migration_card": "миграционную карту",
        "patent": "патент на работу",
        "work_contract": "трудовой договор",
        "other": "документ",
    }
    await state.update_data(pending_doc_type=doc_type)
    await callback.message.answer(
        f"Отправьте {type_names.get(doc_type, 'документ')} (фото или PDF):"
    )


async def handle_extra_doc_upload(
    message: Message, bot: Bot, state: FSMContext, backend: BackendClient
):
    """Загрузить доп.документ."""
    data = await state.get_data()
    token = data.get("access_token", "")
    case_id = data.get("case_id", "")
    doc_type = data.get("pending_doc_type", "other")

    # Поддержка фото и документов
    if message.photo:
        photo = message.photo[-1]
        file = await bot.get_file(photo.file_id)
        buf = io.BytesIO()
        await bot.download(file, destination=buf)
        file_bytes = buf.getvalue()
        filename = f"{doc_type}.jpg"
        content_type = "image/jpeg"
    elif message.document:
        doc = message.document
        file = await bot.get_file(doc.file_id)
        buf = io.BytesIO()
        await bot.download(file, destination=buf)
        file_bytes = buf.getvalue()
        filename = doc.file_name or f"{doc_type}.pdf"
        content_type = doc.mime_type or "application/pdf"
    else:
        await message.answer("Пожалуйста, отправьте фото или файл документа.")
        return

    try:
        await backend.upload_extra_doc(
            token,
            case_id,
            file_bytes,
            doc_type,
            filename,
            content_type,
        )
        await message.answer(
            "✅ Документ загружен.\n\n"
            "Загрузите ещё документы или нажмите Готово:",
            reply_markup=extra_docs_keyboard(),
        )
    except Exception as e:
        logger.error("upload_extra_doc failed: %s", e)
        await message.answer("Ошибка загрузки. Попробуйте ещё раз.")


async def handle_docs_done(callback: CallbackQuery, state: FSMContext, backend: BackendClient):
    """Завершение загрузки документов — показать финальное подтверждение."""
    await callback.answer()
    data = await state.get_data()
    token = data.get("access_token", "")
    case_id = data.get("case_id", "")

    try:
        case = await backend.get_intake_case(token, case_id)
        residents = case.get("residents", [])
        branch = case.get("branch", "")
        branch_label = (
            "Квартира + регистрация"
            if branch == "apartment_registration"
            else "Только регистрация"
        )

        lines = [
            "📋 Итоговые данные заявки:",
            f"Тип: {branch_label}",
            f"Жильцов: {len(residents)}",
            "",
        ]
        for resident in residents:
            fields = (resident.get("ocr_data") or {}).get("fields", {})
            lines.append(
                f"{'👤 (главный) ' if resident.get('is_main') else '👤 '}"
                f"{fields.get('surname', '')} {fields.get('given_names', '')}"
            )

        await state.set_state(IntakeFlow.waiting_final_confirm)
        await callback.message.answer(
            "\n".join(lines),
            reply_markup=final_confirm_keyboard(),
        )
    except Exception as e:
        logger.error("get_intake_case failed: %s", e)
        await callback.message.answer("Ошибка. Попробуйте ещё раз.")


async def handle_final_confirm(
    callback: CallbackQuery, state: FSMContext, backend: BackendClient
):
    """Финальное подтверждение → submit intake."""
    await callback.answer()
    data = await state.get_data()
    token = data.get("access_token", "")
    case_id = data.get("case_id", "")

    try:
        await backend.submit_intake(token, case_id)
        await state.clear()
        await callback.message.answer(
            "✅ Заявка отправлена!\n\n"
            "Менеджер проверит документы и свяжется с вами.\n"
            f"Номер заявки: {case_id[:8]}..."
        )
    except Exception as e:
        logger.error("submit_intake failed: %s", e)
        await callback.message.answer(
            "Не все данные заполнены. Убедитесь что все паспорта подтверждены."
        )


async def handle_restart(callback: CallbackQuery, state: FSMContext):
    """Начать заново."""
    await callback.answer()
    await state.clear()
    await callback.message.answer("Начинаем заново.\n\nВведите ваш номер телефона:")
    await state.set_state(AuthFlow.waiting_phone)
