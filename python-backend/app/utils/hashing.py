"""Hashing helpers for passwords and binary payloads."""

from __future__ import annotations

import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def sha256_hash(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


__all__ = ["hash_password", "verify_password", "sha256_hash", "pwd_context"]
