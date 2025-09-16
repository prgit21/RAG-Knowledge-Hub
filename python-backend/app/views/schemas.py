"""Pydantic schemas for serialising API responses and requests."""

from typing import List, Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class EmbeddingOut(BaseModel):
    id: int
    embedding: List[float]
    content: Optional[str] = None

    class Config:
        orm_mode = True


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


class OpenAIRequest(BaseModel):
    model: str
    input: str


class ImageOut(BaseModel):
    id: int
    url: str
    hash: str
    width: int
    height: int
    embedding: List[float]
    text: Optional[str] = None
    text_embedding: Optional[List[float]] = None

    class Config:
        orm_mode = True
