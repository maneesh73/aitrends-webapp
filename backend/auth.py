from fastapi import Header, HTTPException, status
from config import settings


async def require_sync_auth(x_sync_key: str = Header(default="")):
    if not settings.sync_secret_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sync is disabled: SYNC_SECRET_KEY not set in .env",
        )
    if x_sync_key != settings.sync_secret_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing sync key",
        )
