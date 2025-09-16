"""Application entry-point exposing the FastAPI instance."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text as sa_text
from sqlalchemy.exc import NoSuchTableError

from .controllers import api_router
from .core.clients import minio_client
from .core.config import CORS_ORIGINS, MINIO_BUCKET
from .core.security import pwd_context
from .db import Base, SessionLocal, engine
from .models import User

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    """Initialise database schema, seed default data and ensure storage."""

    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        inspector = inspect(connection)
        table_exists = True
        try:
            columns = {column["name"] for column in inspector.get_columns("images")}
        except NoSuchTableError:
            table_exists = False
            columns = set()
        if table_exists and "text" not in columns:
            connection.execute(sa_text("ALTER TABLE images ADD COLUMN text TEXT"))
        if table_exists and "text_embedding" not in columns:
            connection.execute(
                sa_text("ALTER TABLE images ADD COLUMN text_embedding vector(512)")
            )

    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "user").first():
            db.add(User(username="user", hashed_password=pwd_context.hash("password")))
            db.commit()
    finally:
        db.close()

    if not minio_client.bucket_exists(MINIO_BUCKET):
        minio_client.make_bucket(MINIO_BUCKET)


__all__ = ["app"]
