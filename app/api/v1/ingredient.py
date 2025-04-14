from fastapi import APIRouter, Depends, HTTPException
from app.models.ingredient import Ingredient
from app.dependencies.database import get_db
from app.constants import NUTRIENT_UNITS


router = APIRouter(prefix="/ingredients", tags=["ingredients"])


@router.post("/", response_model=Ingredient)
async def create_ingredient(ingredient: Ingredient, db=Depends(get_db)):
    for nutrient in ingredient.nutrients.keys():
        if nutrient not in NUTRIENT_UNITS:
            raise HTTPException(status_code=422, detail=f"Invalid nutrient: {nutrient}")
    ingredient_dict = ingredient.dict(exclude_unset=True)
    result = await db.ingredients.insert_one(ingredient_dict)
    ingredient_dict["_id"] = str(result.inserted_id)
    return ingredient_dict