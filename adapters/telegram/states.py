from aiogram.fsm.state import State, StatesGroup


class AuthFlow(StatesGroup):
    waiting_phone = State()
    waiting_code = State()


class IntakeFlow(StatesGroup):
    waiting_branch = State()
    waiting_resident_count = State()
    waiting_passport_photo = State()
    waiting_ocr_confirm = State()
    waiting_extra_docs = State()
    waiting_final_confirm = State()
