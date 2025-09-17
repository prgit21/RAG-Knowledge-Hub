"""Pydantic models related to image metadata."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

try:  # pragma: no cover - compatibility shim
    from pydantic import ConfigDict
except ImportError:  # pragma: no cover
    ConfigDict = None


class ImageOut(BaseModel):
    id: int
    url: str
    hash: str
    width: int
    height: int
    embedding: List[float]
    text: Optional[str] = None
    text_embedding: Optional[List[float]] = None

    if ConfigDict is not None:  # pragma: no branch
        model_config = ConfigDict(from_attributes=True)
    else:  # pragma: no cover - legacy support
        class Config:
            orm_mode = True


__all__ = ["ImageOut"]
