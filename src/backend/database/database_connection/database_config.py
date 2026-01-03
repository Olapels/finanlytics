import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
load_dotenv()
db_url = os.getenv("DATABASE_URL_ORIGINAL")


engine = create_async_engine(db_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()
