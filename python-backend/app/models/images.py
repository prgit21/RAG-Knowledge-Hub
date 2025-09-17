"""Database models for image metadata."""

from __future__ import annotations

from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector

from app.db.base import Base


class ImageMetadata(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    hash = Column(String, index=True, nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    embedding = Column(Vector(512))
    text = Column(String, nullable=True)
    text_embedding = Column(Vector(512), nullable=True)


__all__ = ["ImageMetadata"]
