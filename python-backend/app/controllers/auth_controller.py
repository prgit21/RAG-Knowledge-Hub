"""Authentication related API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..core.config import ACCESS_TOKEN_EXPIRE_DELTA
from ..core.security import (
    authenticate_user,
    create_access_token,
    get_current_username,
)
from ..db import get_db
from ..views.schemas import Token

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate a user and issue a JWT access token."""

    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=ACCESS_TOKEN_EXPIRE_DELTA,
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/protected")
async def protected_route(username: str = Depends(get_current_username)):
    """Return a simple message for authenticated users."""

    return {"message": f"Hello, {username}"}
