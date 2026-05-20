from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import random
import string


@dataclass
class PendingAuth:
    phone: str
    code: str
    expires_at: datetime
    attempts: int = 0


_pending: dict[str, PendingAuth] = {}


def generate_code() -> str:
    """4-значный код. В dev режиме возвращает TEST_SMS_CODE из settings."""
    from backend.config import settings

    if settings.TEST_SMS_CODE:
        return settings.TEST_SMS_CODE
    return "".join(random.choices(string.digits, k=4))


def start_auth(phone: str) -> str:
    """Создать/обновить pending auth. Вернуть код (в prod — отправить SMS, вернуть 'sent')."""
    code = generate_code()
    _pending[phone] = PendingAuth(
        phone=phone,
        code=code,
        expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=5),
    )
    return code


def verify_auth(phone: str, code: str) -> bool:
    """Проверить код. Вернуть True если верный и не истёк."""
    pending = _pending.get(phone)
    if not pending:
        return False
    if datetime.now(tz=timezone.utc) > pending.expires_at:
        _pending.pop(phone, None)
        return False
    pending.attempts += 1
    if pending.attempts > 5:
        _pending.pop(phone, None)
        return False
    if pending.code != code:
        return False
    _pending.pop(phone, None)
    return True
