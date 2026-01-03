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
        """Fetch a category id by name scoped to system and optionally user.

        Args:
            db: Database session.
            category_name_in (str): Category name to find.
            user_id (str | None): Optional user scope.

        Returns:
            int | None: Category id if found.
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
        """List category names available to a user (system + user-owned).

        Args:
            db: Database session.
            user_id (str): User identifier.

        Returns:
            list[str]: Available category names.
        """
        categories = await db.execute(select(Category.category_name).where((Category.user_id == user_id) | (Category.user_id == None)))
        return categories.scalars().all()

    async def create_user_category(self, db, user_id: str, category_in: str) -> str:
        """Create a new category for a user, enforcing uniqueness.

        Args:
            db: Database session.
            user_id (str): Owner of the category.
            category_in (str): Category name input.

        Returns:
            str: Normalized category name.

        Raises:
            CategoryAlreadyExistsError: When category already exists.
        """
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
        """Soft-delete a user-owned category if it is not system-defined.

        Args:
            db: Database session.
            user_id (str): Owner id.
            category_id (int): Category identifier.
        """

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
        """Return all active categories (system and user).

        Args:
            db: Database session.

        Returns:
            list[str]: All active category names.
        """
        result = await db.execute(select(Category.category_name).where(Category.is_deleted.is_(False)))
        return result.scalars().all()
