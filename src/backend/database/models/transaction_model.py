from sqlalchemy import Column, String, Float, Date, ForeignKey, Integer, Enum as SqlEnum
from sqlalchemy.orm import relationship
from backend.database.database_connection.database_client import Base
from enum import Enum

class TransactionTypeEnum(Enum):
    INCOME = "income"
    EXPENSE = "expense"

class Transactions(Base):
    __tablename__ = "transactions"
    transaction_id = Column(String, primary_key=True, index=True)
    user_id = Column(String,ForeignKey("users.user_id"), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(SqlEnum(TransactionTypeEnum), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    to_from = Column(String, nullable=False)
    description = Column(String, nullable=False)

    #defining relationships to user and category
    category = relationship("Category", back_populates="transactions") #category.transactions each category has many transactions
    user = relationship("User", back_populates="transactions") #user.transactions a user has many transactions
