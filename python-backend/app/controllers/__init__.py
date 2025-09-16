"""FastAPI routers grouped by feature area."""

from fastapi import APIRouter

from .auth_controller import router as auth_router
from .embedding_controller import router as embedding_router
from .image_controller import router as image_router
from .system_controller import router as system_router

api_router = APIRouter()
api_router.include_router(system_router)
api_router.include_router(auth_router)
api_router.include_router(embedding_router)
api_router.include_router(image_router)

__all__ = ["api_router"]
