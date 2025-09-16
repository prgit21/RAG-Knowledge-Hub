"""Central configuration for the FastAPI backend."""

import os
from datetime import timedelta
from typing import List

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9001")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "images")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1/responses")

CORS_ORIGINS: List[str] = [
    "http://localhost:9000",
    "http://localhost:4200",
    "http://localhost:4201",
    "http://localhost:8080",
]
