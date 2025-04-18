from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import datetime
from app.models.ingredient import Ingredient

class MealIngredient(BaseModel):
    ingredient: Union[str, Ingredient]  # Either an ingredient ID (str) or full Ingredient data
    quantity: float

class IngredientInMeal(BaseModel):
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

class MealListItem(BaseModel):
    id: str = Field(..., alias='_id')
    user_id: str
    name: str
    description: Optional[str] = None
    ingredients: List[IngredientInMeal]  # Use IngredientInMeal for listing
    timestamp: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PaginatedMeals(BaseModel):
    meals: List[MealListItem]
    total: int
    page: int
    page_size: int