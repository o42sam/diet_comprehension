from fastapi import APIRouter, Depends, HTTPException
from app.models.ingredient import Ingredient
from app.services.ingredient import create_ingredient, get_ingredients, search_ingredients
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.exceptions.ingredient import IngredientCreationError, IngredientAlreadyExistsError, IngredientSearchError
from typing import List

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

@router.post("/", response_model=Ingredient)
async def create_new_ingredient(
    ingredient: Ingredient,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        return await create_ingredient(db, ingredient)
    except IngredientAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except IngredientCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Ingredient])
async def list_ingredients(
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        return await get_ingredients(db)
    except IngredientCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search", response_model=List[Ingredient])
async def search_ingredients_endpoint(
    query: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        return await search_ingredients(db, query)
    except IngredientSearchError as e:
        raise HTTPException(status_code=500, detail=str(e))