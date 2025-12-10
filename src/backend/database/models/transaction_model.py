from sqlalchemy import Column, String, Float
from database.database_connection.database_client import Base

class Transactions(Base):
    __tablename__ = "transactions"
    transaction_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, nullable=False)
    date = Column(String, nullable=False)
    time = Column(String, nullable=True)
    money_in = Column(Float, nullable=False)
    money_out = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    to_from = Column(String, nullable=False)
    description = Column(String, nullable=False)
    balance = Column(Float, nullable=False)
