from datetime import datetime, timedelta, timezone

import jwt as pyjwt

from backend.config import settings

ALGORITHM = "HS256"


def create_access_token(phone: str) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": phone,
        "type": "client",
        "iat": now,
        "exp": now + timedelta(hours=24),
    }
    return pyjwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    return pyjwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
