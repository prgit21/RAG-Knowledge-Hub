"""FastAPI application setup and router composition."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text as sa_text
from sqlalchemy.exc import NoSuchTableError

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.repositories.users_repo import UserRepository
from app.routers import auth, images, search
from app.utils.hashing import hash_password
from app.utils.storage import get_storage_client


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI()

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    include_routers(application)

    @application.on_event("startup")
    def on_startup() -> None:
        init_database()
        init_default_user()
        get_storage_client().ensure_bucket()

    @application.get("/api/hello")
    async def read_hello() -> dict[str, str]:
        return {"message": "Hello from FastAPI"}

    return application


def include_routers(application: FastAPI) -> None:
    application.include_router(auth.router)
    application.include_router(images.router)
    application.include_router(search.router)


def init_database() -> None:
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


def init_default_user() -> None:
    session = SessionLocal()
    try:
        repository = UserRepository(session)
        if repository.get_by_username("user") is None:
            repository.create(
                username="user",
                hashed_password=hash_password("password"),
            )
    finally:
        session.close()


app = create_app()


__all__ = ["create_app", "app"]
