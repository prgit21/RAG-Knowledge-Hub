"""User model definition."""

from sqlalchemy import Column, Integer, String

from ..db import Base


class User(Base):
    """Represents an authenticated user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
