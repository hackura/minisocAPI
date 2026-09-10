from fastapi import Header, HTTPException, status
from app.config import API_KEY

def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key",
        )
    return x_api_key
