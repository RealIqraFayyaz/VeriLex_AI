
import jwt

from datetime import datetime, timedelta, timezone

from pwdlib import PasswordHash

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database import get_db
from app.models import User


hasher = PasswordHash.recommended()

oauth = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login"
)


def hash_password(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("Password cannot be empty")

    return hasher.hash(value)


def verify_password(value: str, hashed: str) -> bool:
    if not isinstance(value, str) or not isinstance(hashed, str):
        return False

    try:
        return hasher.verify(value, hashed)
    except Exception:
        return False


def make_token(uid: int) -> str:
    if not isinstance(uid, int) or uid <= 0:
        raise ValueError("Invalid user ID")

    now = datetime.now(timezone.utc)

    exp = now + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload = {
        "sub": str(uid),
        "iat": now,
        "exp": exp,
        "type": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm="HS256",
    )


async def current_user(
    token: str = Depends(oauth),
    db: AsyncSession = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=["HS256"],
            options={
                "require": ["sub", "exp", "iat", "type"]
            },
        )

        if payload.get("type") != "access":
            raise ValueError("Invalid token type")

        uid = int(payload["sub"])

        if uid <= 0:
            raise ValueError("Invalid user ID")

    except (
        jwt.InvalidTokenError,
        ValueError,
        TypeError,
        KeyError,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.scalar(
        select(User).where(
            User.id == uid,
            User.is_active.is_(True),
        )
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def roles(*allowed):
    async def check(
        user: User = Depends(current_user),
    ):
        if user.role not in allowed:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions",
            )

        return user

    return check
