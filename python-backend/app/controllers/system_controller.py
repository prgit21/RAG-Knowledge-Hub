"""Miscellaneous application endpoints."""

import requests
from fastapi import APIRouter, HTTPException

from ..core.config import OPENAI_API_KEY, OPENAI_API_URL
from ..views.schemas import OpenAIRequest

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/hello")
async def read_hello():
    """Return a simple greeting used for health checks."""

    return {"message": "Hello from FastAPI"}


@router.post("/openai")
def call_openai(request: OpenAIRequest):
    """Proxy a request to the OpenAI responses endpoint."""

    api_key = OPENAI_API_KEY
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {"model": request.model, "input": request.input}

    response = requests.post(OPENAI_API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    return response.json()
