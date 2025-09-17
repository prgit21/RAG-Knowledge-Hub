"""Authentication API routes."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.db.session import get_db
from app.models.users import User
from app.schemas.auth import Token

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    settings = get_settings()
    access_token = create_access_token(
        subject=user.username,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": f"Hello, {current_user.username}"}


__all__ = ["router"]
