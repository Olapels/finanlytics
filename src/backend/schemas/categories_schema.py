from pydantic import BaseModel, Field

#category input from user
class CategoryCreate(BaseModel):
    category_name: str = Field(description="Name of the category.")

class CategoryOut(CategoryCreate):
    category_id: int = Field(description="Unique identifier for the category.")

    class Config:
        from_attributes = True 