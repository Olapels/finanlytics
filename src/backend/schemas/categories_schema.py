from pydantic import BaseModel, Field,ConfigDict

#category input from user
class CategoryCreate(BaseModel):
    category_name: str = Field(description="Name of the category.")

class CategoryOut(CategoryCreate):
    category_id: int = Field(description="Unique identifier for the category.")

    model_config = ConfigDict(from_attributes=True) 