"""Pydantic schemas for embedding and search operations."""

from __future__ import annotations

from typing import Dict, List

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


class RetrieveQuery(BaseModel):
    query: str
    k: int = 3


class RetrievedItem(BaseModel):
    id: int
    url: str
    width: int
    height: int
    score: float
    ocr_text: str | None = None
    modalities_used: List[str]
    distances: Dict[str, float]
    similarities: Dict[str, float]

    if ConfigDict is not None:  # pragma: no branch
        model_config = ConfigDict(from_attributes=True)
    else:  # pragma: no cover - legacy support
        class Config:
            orm_mode = True


__all__ = [
    "EmbeddingOut",
    "AskRequest",
    "AskResponse",
    "OpenAIRequest",
    "RetrieveQuery",
    "RetrievedItem",
]
