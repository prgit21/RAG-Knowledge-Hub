"""Image metadata model definition."""

from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector

from ..db import Base


class ImageMetadata(Base):
    """Stores metadata and embeddings for uploaded images."""

    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    hash = Column(String, index=True)
    width = Column(Integer)
    height = Column(Integer)
    embedding = Column(Vector(512))
    text = Column(String, nullable=True)
    text_embedding = Column(Vector(512), nullable=True)
