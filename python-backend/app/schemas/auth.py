"""Pydantic models related to authentication."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

try:  # pragma: no cover - compatibility shim
    from pydantic import ConfigDict
except ImportError:  # pragma: no cover - fallback for Pydantic v1
    ConfigDict = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    if ConfigDict is not None:  # pragma: no branch - runtime configuration
        model_config = ConfigDict(from_attributes=True)
    else:  # pragma: no cover - legacy Pydantic v1 support
        class Config:
            orm_mode = True


__all__ = [
    "Token",
    "TokenData",
    "UserBase",
    "UserCreate",
    "UserOut",
]
