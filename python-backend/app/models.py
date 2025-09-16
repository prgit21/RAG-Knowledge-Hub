from sqlalchemy import Column, Integer, String
from pgvector.sqlalchemy import Vector
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=True)
    embedding = Column(Vector(3))


class ImageMetadata(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    hash = Column(String, index=True)
    width = Column(Integer)
    height = Column(Integer)
    embedding = Column(Vector(512))
    text = Column(String, nullable=True)
    text_embedding = Column(Vector(512), nullable=True)
