from sqlalchemy import Column, String, DateTime
from database.database_connection.database_client import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False,unique=True)
    password = Column(String, nullable=False)
    create_date = Column(DateTime(timezone=True), nullable=False) 
