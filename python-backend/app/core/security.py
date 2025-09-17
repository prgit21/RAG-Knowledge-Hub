"""Security helpers for authentication and authorization."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.users import User
from app.repositories.users_repo import UserRepository
from app.utils.hashing import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    repo = UserRepository(db)
    user = repo.get_by_username(username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    settings = get_settings()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError as exc:  # pragma: no cover - defensive branch
        raise credentials_exception from exc
    repo = UserRepository(db)
    user = repo.get_by_username(username)
    if user is None:
        raise credentials_exception
    return user


__all__ = [
    "authenticate_user",
    "create_access_token",
    "get_current_user",
    "oauth2_scheme",
]
