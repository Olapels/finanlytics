from sqlalchemy import Column,Integer, String,Boolean,ForeignKey, DateTime,UniqueConstraint,select
from backend.database.database_connection.database_client import Base
from sqlalchemy.orm import relationship
from sqlalchemy.ext.asyncio import AsyncSession
import datetime

DEFAULT_CATEGORIES = [
    "Food & Groceries",
    "Dining Out",
    "Transport",
    "Shopping",
    "Rent / Mortgage",
    "Utilities",
    "Health",
    "Entertainment",
    "Subscriptions",
    "Savings",
    "Income",
    "Miscellaneous"
]

class Category(Base):
    __tablename__ = "categories"
    category_id = Column(Integer, primary_key=True)
    category_name = Column(String, nullable=False)
    user_id = Column(String,ForeignKey("users.user_id"), nullable=True)
    create_date = Column(DateTime(timezone=True), nullable=False)
    is_system = Column(Boolean, default=False, nullable=False) 
    is_deleted = Column(Boolean, default=False, nullable=False)

    #defining relationships to user and transactions
    owner = relationship("User", back_populates="categories") #user.categories a user has many categories
    transactions = relationship("Transactions", back_populates="category") #category.transactions each category has many transactions

    __table_args__ = (
        # Prevent duplicate category names per user
        UniqueConstraint("category_name", "user_id", name="uq_category_name_per_user"),
    )

#seed default categories for system (user_id=None) categories
async def seed_categories(session: AsyncSession) -> None:
    result = await session.execute(
        select(Category.category_name).where(
            Category.user_id == None,
            Category.is_system == True,
        )
    )

    existing = set(result.scalars().all())

    for name in DEFAULT_CATEGORIES:
        if name not in existing:
            session.add(
                Category(
                    category_name=name,
                    user_id=None,
                    is_system=True,
                    create_date=datetime.datetime.now(datetime.timezone.utc),
                ),
            )

    await session.commit()
