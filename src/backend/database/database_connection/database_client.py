from database.database_connection.database_config import AsyncSessionLocal, Base, engine

async def init_db() -> None:
    # Import all models to register them with Base
    from database.models import user_model,transaction_model,categories_model  
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Seed categories after tables are created
    from database.models.categories_model import seed_categories

    async with AsyncSessionLocal() as session:
        await seed_categories(session)
    
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
