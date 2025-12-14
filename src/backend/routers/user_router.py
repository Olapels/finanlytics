from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated

from services.user_service import user_service
from schemas.user_schema import (
    UserCreateSchema,
    UserLoginSchema,
    UserResponseSchema,
)
from database.database_connection.database_client import get_db

user_router = APIRouter()


@user_router.post("/register", response_model=UserResponseSchema)
async def register_user(
    user_in: UserCreateSchema,
    db=Depends(get_db),
):
    existing_user = await user_service.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists",
        )

    user = await user_service.create_user(db, user_in)
    return user


@user_router.post("/login")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(get_db),
):
    user = await user_service.get_user_by_email(db, form_data.username)

    if not user or not user_service.verify_password(
        form_data.password, user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = user_service.create_access_token(subject=user.user_id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@user_router.get("/me", response_model=UserResponseSchema)
async def get_me(
    current_user=Depends(user_service.get_current_user),
):
    return current_user


@user_router.post("/logout")
async def logout():
    """
    JWT logout is handled client-side by deleting the token.
    """
    return {"message": "Logged out successfully"}

    
