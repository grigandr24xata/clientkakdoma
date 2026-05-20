import jwt as pyjwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.auth.jwt import decode_access_token

bearer = HTTPBearer()


def get_current_phone(credentials: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    try:
        payload = decode_access_token(credentials.credentials)
        phone: str | None = payload.get("sub")
        if not phone:
            raise HTTPException(status_code=401, detail="Invalid token")
        return phone
    except pyjwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired") from exc
    except pyjwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
