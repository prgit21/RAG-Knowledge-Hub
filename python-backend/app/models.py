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
    __tablename__ = "image_metadata"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    hash = Column(String, unique=True)
    width = Column(Integer)
    height = Column(Integer)