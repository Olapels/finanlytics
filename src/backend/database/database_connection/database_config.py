import os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
db_url = os.getenv("DATABASE_URL_ORIGINAL")
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Fetch database connection details
USER = os.getenv("db_user")
PASSWORD = os.getenv("db_password")
HOST = os.getenv("db_host")
PORT = os.getenv("db_port")
DBNAME = os.getenv("dbname")

# SQLAlchemy connection string
DATABASE_URL = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

# Create the SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=False)

async def test_connection():
    try:
        async with engine.connect() as connection:
            print("Connection successful!")
    except Exception as e:
        print(f"Failed to connect: {e}")

asyncio.run(test_connection())

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()
