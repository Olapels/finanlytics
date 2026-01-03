from datetime import datetime, timezone, timedelta
from uuid import uuid4
from typing import Optional

import jwt
from jwt import PyJWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
import os
from dotenv import load_dotenv
load_dotenv()

from backend.database.models import User
from backend.database.database_connection.database_client import get_db

#for some of my highlevel security services implement stored procedures 
#ORMs under the hood use parameterized sql queries that preject SQL injection attacks
#will implement more security long term

password_hash = PasswordHash.recommended()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

SECRET_KEY = os.environ["SECRET_KEY"]
ALGORITHM = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class UserService:
    """Service for user authentication and management"""

    async def create_user(self, db: AsyncSession, user_in):
        hashed_password = self.hash_password(user_in.password)

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

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, db: AsyncSession, user_id: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    def hash_password(password: str) -> str:
        return password_hash.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return password_hash.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        subject: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        expire = datetime.now(timezone.utc) + (
            expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode = {"sub": subject, "exp": expire}
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> dict:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    async def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db),
    ) -> User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = self.decode_token(token)
            user_id: str | None = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except PyJWTError:
            raise credentials_exception

        user = await self.get_user_by_id(db, user_id)
        if user is None:
            raise credentials_exception

        return user


user_service = UserService()
