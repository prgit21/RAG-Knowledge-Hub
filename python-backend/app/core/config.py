"""Application configuration utilities."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()


def _str_to_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in {"1", "true", "t", "yes", "y"}


def _get_required_env(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise RuntimeError(f"{key} environment variable is not set")
    return value


def _get_cors_origins() -> List[str]:
    raw_origins = os.getenv("CORS_ORIGINS")
    if raw_origins:
        return [origin.strip() for origin in raw_origins.split(",") if origin.strip()]
    return [
        "http://localhost:9000",
        "http://localhost:4200",
        "http://localhost:4201",
        "http://localhost:8080",
    ]


@dataclass(slots=True)
class Settings:
    """Typed application settings sourced from environment variables."""

    database_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    s3_access_key_id: Optional[str] = None
    s3_secret_access_key: Optional[str] = None
    s3_bucket: str = "images"
    s3_region: Optional[str] = None
    s3_endpoint_url: Optional[str] = None
    s3_use_path_style: bool = False
    cors_origins: List[str] = field(default_factory=_get_cors_origins)
    openai_api_url: str = "https://api.openai.com/v1/responses"
    openai_chat_api_url: str = "https://api.openai.com/v1/chat/completions"
    openai_api_key: Optional[str] = None
    create_demo_user: bool = False


@lru_cache
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    return Settings(
        database_url=_get_required_env("DATABASE_URL"),
        jwt_secret=_get_required_env("JWT_SECRET"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        ),
        s3_access_key_id=os.getenv("S3_ACCESS_KEY_ID"),
        s3_secret_access_key=os.getenv("S3_ACCESS_KEY"),
        s3_bucket=os.getenv("S3_BUCKET", "images"),
        s3_region=os.getenv("S3_REGION"),
        # s3_endpoint_url=os.getenv("S3_ENDPOINT_URL"),
        # s3_use_path_style=_str_to_bool(os.getenv("S3_USE_PATH_STYLE"), False),
        cors_origins=_get_cors_origins(),
        openai_api_url=os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/responses"),
        openai_chat_api_url=os.getenv(
            "OPENAI_CHAT_API_URL", "https://api.openai.com/v1/chat/completions"
        ),
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        create_demo_user=_str_to_bool(os.getenv("CREATE_DEMO_USER"), False),
    )


__all__ = ["Settings", "get_settings"]
