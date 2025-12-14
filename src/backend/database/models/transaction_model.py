from sqlalchemy import Column, String, Float,Date,ForeignKey
from database.database_connection.database_client import Base

class Transactions(Base):
    __tablename__ = "transactions"
    transaction_id = Column(String, primary_key=True, index=True)
    user_id = Column(String,ForeignKey("users.user_id"), nullable=False)
    date = Column(Date, nullable=False)
    money_in = Column(Float, nullable=False)
    money_out = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    to_from = Column(String, nullable=False)
    description = Column(String, nullable=False)
    balance = Column(Float, nullable=False)
