from typing import List

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


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
    content: str | None = None


    class Config:
        orm_mode = True


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str