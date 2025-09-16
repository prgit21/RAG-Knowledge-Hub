"""Authentication helpers and shared security utilities."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from ..models import User
from .config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_SECRET

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Validate the supplied credentials and return the user if valid."""

    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None
    if not pwd_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed JWT token for the supplied payload."""

    if not JWT_SECRET:
        raise RuntimeError("JWT_SECRET environment variable is not set")

    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


def get_username_from_token(token: str) -> str:
    """Extract the username from a JWT token, raising if invalid."""

    if not JWT_SECRET:
        raise HTTPException(status_code=500, detail="JWT secret is not configured")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError as exc:  # pragma: no cover - defensive branch
        raise HTTPException(status_code=401, detail="Invalid token") from exc


def get_current_username(token: str = Depends(oauth2_scheme)) -> str:
    """FastAPI dependency that returns the username for the supplied token."""

    return get_username_from_token(token)
