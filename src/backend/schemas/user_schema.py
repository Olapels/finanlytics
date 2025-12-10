from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    user_id: str
    email: EmailStr
    password: str
    first_name: str 
    last_name: str
    create_date : datetime


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str   

class UserResponseSchema(BaseModel):
    email: EmailStr
    first_name: str 
    last_name: str
    password: str



