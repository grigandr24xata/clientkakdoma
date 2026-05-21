import asyncio
import logging

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage

from adapters.telegram.backend_client import BackendClient
from adapters.telegram.config import BOT_TOKEN
from adapters.telegram.handlers import (
    cmd_start,
    handle_branch_select,
    handle_code_input,
    handle_docs_done,
    handle_extra_doc_type,
    handle_extra_doc_upload,
    handle_final_confirm,
    handle_ocr_confirm,
    handle_passport_photo,
    handle_phone_input,
    handle_resident_count,
    handle_restart,
)
from adapters.telegram.states import AuthFlow, IntakeFlow

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def setup_router(dp: Dispatcher, backend: BackendClient) -> None:
    """Регистрация всех handlers."""

    # Инжектировать backend через lambda
    dp.message.register(
        lambda msg, state: cmd_start(msg, state, backend),
        CommandStart(),
    )

    # Auth flow
    dp.message.register(
        lambda msg, state: handle_phone_input(msg, state, backend),
        AuthFlow.waiting_phone,
    )
    dp.message.register(
        lambda msg, state: handle_code_input(msg, state, backend),
        AuthFlow.waiting_code,
    )

    # Branch selection
    dp.callback_query.register(
        lambda cb, state: handle_branch_select(cb, state, backend),
        F.data.startswith("branch_"),
        IntakeFlow.waiting_branch,
    )

    # Resident count
    dp.callback_query.register(
        lambda cb, state: handle_resident_count(cb, state, backend),
        F.data.startswith("count_"),
        IntakeFlow.waiting_resident_count,
    )

    # Passport upload
    dp.message.register(
        lambda msg, bot, state: handle_passport_photo(msg, bot, state, backend),
        IntakeFlow.waiting_passport_photo,
        F.photo,
    )
    dp.message.register(
        lambda msg, state: msg.answer("Пожалуйста, отправьте фото паспорта."),
        IntakeFlow.waiting_passport_photo,
    )

    # OCR confirm
    dp.callback_query.register(
        lambda cb, state: handle_ocr_confirm(cb, state, backend),
        F.data.in_({"ocr_confirm", "ocr_confirm_manual", "ocr_retake"}),
        IntakeFlow.waiting_ocr_confirm,
    )

    # Extra docs — выбор типа
    dp.callback_query.register(
        lambda cb, state: handle_extra_doc_type(cb, state),
        F.data.startswith("doc_") & ~F.data.startswith("docs_"),
        IntakeFlow.waiting_extra_docs,
    )

    # Extra docs — загрузка файла
    dp.message.register(
        lambda msg, bot, state: handle_extra_doc_upload(msg, bot, state, backend),
        IntakeFlow.waiting_extra_docs,
        F.photo | F.document,
    )

    # Extra docs — готово
    dp.callback_query.register(
        lambda cb, state: handle_docs_done(cb, state, backend),
        F.data == "docs_done",
        IntakeFlow.waiting_extra_docs,
    )

    # Final confirm
    dp.callback_query.register(
        lambda cb, state: handle_final_confirm(cb, state, backend),
        F.data == "final_confirm",
        IntakeFlow.waiting_final_confirm,
    )

    # Restart (работает из любого состояния)
    dp.callback_query.register(
        lambda cb, state: handle_restart(cb, state),
        F.data == "restart",
    )


async def main() -> None:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set. Add it to .env")

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Создать один shared aiohttp session и BackendClient
    async with aiohttp.ClientSession() as http_session:
        backend = BackendClient(http_session)
        setup_router(dp, backend)

        logger.info("Telegram adapter starting...")
        try:
            await dp.start_polling(bot)
        finally:
            await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
