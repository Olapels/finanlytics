from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.database_connection.database_client import get_db
from backend.services.category_service import CategoryService, CategoryAlreadyExistsError
from backend.services.user_service import user_service
from backend.database.models import User
from backend.schemas.categories_schema import CategoryCreate, CategoryOut
from typing import List, Dict


category_router = APIRouter()


@category_router.get("/user_categories", response_model=list[str])
async def get_user_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user)
):
    """Return system and user-created categories for the authenticated user.

    Args:
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        list[str]: Available categories.
    """
    user_id = current_user.user_id
    categories = await CategoryService().get_user_categories(db, user_id)
    return categories

@category_router.post("/create_category", response_model=str)
async def create_user_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(user_service.get_current_user),
):
    """Create a new category for the current user.

    Args:
        category_in (CategoryCreate): Category payload.
        db (AsyncSession): Database session.
        current_user (User): Authenticated user.

    Returns:
        str: Created category name.
    """
    user_id = current_user.user_id
    try:
        create_status = await CategoryService().create_user_category(db, user_id, category_in)
    except CategoryAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Category already exists.")
    return create_status
