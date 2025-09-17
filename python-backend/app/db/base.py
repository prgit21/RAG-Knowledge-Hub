"""Base metadata for SQLAlchemy models."""

from __future__ import annotations

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models to ensure they are registered with SQLAlchemy's metadata.
# pylint: disable=unused-import
from app.models import embeddings, images, users  # noqa: E402,F401

__all__ = ["Base"]
