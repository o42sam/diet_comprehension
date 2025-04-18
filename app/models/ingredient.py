from pydantic import BaseModel, Field
from typing import Optional, Dict

class Ingredient(BaseModel):
    id: str = Field(..., alias='_id')
    name: str
    description: Optional[str] = None
    quantity: float
    unit: float
    reference_quantity: float
    reference_unit: str
    nutrients: Dict[str, float]