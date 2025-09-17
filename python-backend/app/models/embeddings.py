"""Database models for embedding storage."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=True)
    embedding = Column(Vector(3))


__all__ = ["Embedding"]
