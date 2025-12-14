from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreateSchema(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponseSchema(BaseModel):
    user_id: str
    email: EmailStr
    first_name: str
    last_name: str
    create_date: datetime

    class Config:
        from_attributes = True




