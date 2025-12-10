from database.database_connection.database_config import AsyncSessionLocal, Base, engine

async def init_db() -> None:
    from database.models import user_model
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
