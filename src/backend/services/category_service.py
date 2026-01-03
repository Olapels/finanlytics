from typing import Optional, List, Dict
from backend.database.models.categories_model import Category
from backend.schemas.categories_schema import CategoryCreate
import datetime
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


class CategoryAlreadyExistsError(Exception):
    pass

class CategoryService:
    async def get_category_by_name(self, db, category_name_in: str, user_id: Optional[str] = None) -> Optional[int]:
        """
        Return the category_id for the given name scoped to the user (or system).
        """
        # normalized = category_name_in.strip().lower()
        query = select(Category.category_id).where(
            Category.category_name == category_name_in,
            Category.is_deleted == False,
        )
        if user_id:
            query = query.where((Category.user_id == user_id) | (Category.user_id == None))
        result = await db.execute(query)
        category_id = result.scalar_one_or_none()
        return category_id
    
    async def get_user_categories(self, db, user_id: str) -> List[Dict]:
        categories = await db.execute(select(Category.category_name).where((Category.user_id == user_id) | (Category.user_id == None)))
        return categories.scalars().all()

    async def create_user_category(self, db, user_id: str, category_in: str) -> str:
        normalized_name = category_in.lower()
        stmt = select(Category).where(
            (Category.user_id == user_id) &
            (Category.category_name == normalized_name) &
            (Category.is_deleted.is_(False))
        )

        if (await db.execute(stmt)).scalar_one_or_none():
            raise CategoryAlreadyExistsError()

        new_category = Category(
            category_name=normalized_name,
            user_id=user_id,
            create_date=datetime.now(timezone.utc),
            is_system=False,
            is_deleted=False
        )

        try:
            db.add(new_category)
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise CategoryAlreadyExistsError()

        # return f"Category created successfully: {normalized_name}"
        return normalized_name

    


    async def delete_user_category(
        self,
        db,
        user_id: str,
        category_id: int
    ) -> None:

        stmt = select(Category).where(
            (Category.category_id == category_id) &
            (Category.user_id == user_id) &
            (Category.is_system.is_(False)) &
            (Category.is_deleted.is_(False))
        )

        result = await db.execute(stmt)
        category_obj = result.scalar_one_or_none()

        if not category_obj:
            raise Exception("Category not found or cannot be deleted.")

        try:
            category_obj.is_deleted = True
            await db.commit()
        except Exception:
            await db.rollback()
            raise
    

    async def get_all_categories(self, db) -> List:
        result = await db.execute(select(Category.category_name).where(Category.is_deleted.is_(False)))
        return result.scalars().all()
