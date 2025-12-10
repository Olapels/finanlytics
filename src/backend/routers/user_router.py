from fastapi import FastAPI, Depends, HTTPException,APIRouter
from services.user_service import user_service
from services.security_service import auth_service
from schemas.user_schema import UserResponseSchema,UserLoginSchema
from database.database_connection.database_client import get_db
user_router = APIRouter()

@user_router.post("/login")
async def login(
    request: UserLoginSchema,
    db: get_db = Depends()
):
    user = await user_service.get_user_by_email(db, request.email)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not auth_service.verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    return {
        "success": True,
        "message": "Login successful",
        "token": f"token_{user.user_id}",
        "user": {
            "id": user.user_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    }    

@user_router.post("/register")
async def register_user(user_in: UserResponseSchema, db:get_db = Depends()):
    if not user_in.email or not user_in.password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    existing_user = await user_service.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists") 
    user = await user_service.create_user(db, user_in)
    return user

@user_router.post("/logout")
async def logout():
    """Logout endpoint."""
    return {"message": "Logged out successfully"}
    
