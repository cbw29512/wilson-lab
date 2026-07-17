from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import Settings
from .models import User, UserRole

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def authenticate_user(database: Session, username: str, password: str) -> User | None:
    user = database.scalar(select(User).where(User.username == username))
    if not user or not user.is_active:
        return None
    if not password_hash.verify(password, user.password_hash):
        return None
    user.last_login_at = datetime.now(timezone.utc)
    database.commit()
    database.refresh(user)
    return user


def create_access_token(user: User, settings: Settings) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_minutes)
    payload = {
        "sub": user.username,
        "role": user.role,
        "exp": expires_at,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.InvalidTokenError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error


def seed_demo_users(database: Session, settings: Settings) -> None:
    if not settings.seed_demo_users:
        return

    demo_users = (
        (settings.viewer_username, settings.viewer_password, UserRole.VIEWER),
        (settings.admin_username, settings.admin_password, UserRole.ADMIN),
    )
    changed = False

    for username, password, role in demo_users:
        existing = database.scalar(select(User).where(User.username == username))
        if existing:
            continue
        database.add(
            User(
                username=username,
                password_hash=hash_password(password),
                role=role,
            )
        )
        changed = True

    if changed:
        database.commit()
