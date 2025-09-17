"""Pydantic schemas for embedding and search operations."""

from __future__ import annotations

from typing import List

from pydantic import BaseModel

try:  # pragma: no cover - compatibility shim
    from pydantic import ConfigDict
except ImportError:  # pragma: no cover
    ConfigDict = None


class EmbeddingOut(BaseModel):
    id: int
    embedding: List[float]
    content: str | None = None

    if ConfigDict is not None:  # pragma: no branch
        model_config = ConfigDict(from_attributes=True)
    else:  # pragma: no cover - legacy support
        class Config:
            orm_mode = True


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


class OpenAIRequest(BaseModel):
    model: str
    input: str


__all__ = ["EmbeddingOut", "AskRequest", "AskResponse", "OpenAIRequest"]
