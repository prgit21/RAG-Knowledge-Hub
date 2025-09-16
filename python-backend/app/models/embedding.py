"""Embedding model definition."""

from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector

from ..db import Base


class Embedding(Base):
    """Stores vector embeddings linked to optional content."""

    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=True)
    embedding = Column(Vector(3))
