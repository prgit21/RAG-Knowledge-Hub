"""Data-access helpers for user records."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models.users import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_username(self, username: str) -> Optional[User]:
        return (
            self._session.query(User)
            .filter(User.username == username)
            .first()
        )

    def create(self, username: str, hashed_password: str) -> User:
        user = User(username=username, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user


__all__ = ["UserRepository"]
