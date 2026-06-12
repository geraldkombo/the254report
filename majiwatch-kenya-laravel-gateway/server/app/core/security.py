from fastapi import Header, HTTPException

from app.core.config import settings


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    if x_api_key is None or x_api_key != settings.api_key_change_me:
        raise HTTPException(status_code=401, detail="Invalid API key")

