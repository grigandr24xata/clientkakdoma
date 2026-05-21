from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def branch_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏠 Квартира + регистрация",
                    callback_data="branch_apartment_registration",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📋 Только регистрация",
                    callback_data="branch_registration_only",
                )
            ],
        ]
    )


def resident_count_keyboard(max_count: int = 10) -> InlineKeyboardMarkup:
    rows = []
    row = []
    for i in range(1, min(max_count + 1, 11)):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"count_{i}"))
        if len(row) == 5:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def ocr_confirm_keyboard(needs_review: bool = False) -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(text="✅ Всё верно", callback_data="ocr_confirm")]]
    if needs_review:
        rows.append(
            [
                InlineKeyboardButton(
                    text="⚠️ Подтвердить с замечанием",
                    callback_data="ocr_confirm_manual",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="🔄 Переснять", callback_data="ocr_retake")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def extra_docs_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🪪 Миграционная карта", callback_data="doc_migration_card"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 Патент на работу", callback_data="doc_patent"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Трудовой договор", callback_data="doc_work_contract"
                )
            ],
            [InlineKeyboardButton(text="📎 Другой документ", callback_data="doc_other")],
            [InlineKeyboardButton(text="✅ Готово, отправить", callback_data="docs_done")],
        ]
    )


def final_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Подтвердить и отправить", callback_data="final_confirm"
                )
            ],
            [InlineKeyboardButton(text="❌ Начать заново", callback_data="restart")],
        ]
    )
