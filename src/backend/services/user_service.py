from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.user_schema import UserCreate, UserResponseSchema
from services.security_service import auth_service
from database.models.user_model import User

class UserService:
    async def create_user(self, db: AsyncSession, user_in: UserResponseSchema):
        hashed_password = auth_service.hash_password(user_in.password)
        user = User(
            user_id=str(uuid4()),
            email=user_in.email,
            password=hashed_password,
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            create_date=datetime.now(timezone.utc),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    async def get_user_by_email(self, db: AsyncSession, email: str):
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_user_by_id(self, db: AsyncSession, user_id: str):
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()


user_service = UserService()
