from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS middleware for frontend-backend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers.user_router import user_router
from routers.transaction_router import transaction_router
from database.database_connection.database_client import init_db

app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(transaction_router, prefix="/transactions", tags=["transactions"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
def home():
    return "Welcome to my EduTrack Lite API"
