from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class MealIngredient(BaseModel):
    ingredient_id: str
    quantity: float

class Meal(BaseModel):
    id: str = Field(..., alias='_id')
    user_id: str
    name: str
    description: Optional[str] = None
    ingredients: List[MealIngredient]
    timestamp: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MealListItem(Meal):
    id: str = Field(..., alias='_id')
    user_id: str
    
class PaginatedMeals(BaseModel):
    meals: List[MealListItem]
    total: int
    page: int
    page_size: int