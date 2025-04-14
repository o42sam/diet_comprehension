from fastapi import APIRouter, Depends, HTTPException, Query
from app.models.meal import Meal, MealListItem, PaginatedMeals
from app.services.meal import create_meal_entry, get_last_meal_entry_by_user, get_paginated_meals_by_user, get_detailed_meal
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.exceptions.meal import MealNotFoundError, MealCreationError, MealValidationError
from bson import ObjectId

router = APIRouter(prefix="/meals", tags=["meals"])


@router.post("/", response_model=MealListItem)
async def create_meal(meal: Meal, user_id: str = Depends(get_current_user), db=Depends(get_db)):
    try:
        return await create_meal_entry(db, meal, user_id)
    except MealCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except MealValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/last", response_model=MealListItem)
async def get_last_meal_by_user(user_id: str = Depends(get_current_user), db=Depends(get_db)):
    try:
        return await get_last_meal_entry_by_user(db, user_id)
    except MealNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MealCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except MealValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    
@router.get("/", response_model=PaginatedMeals)
async def get_meals(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    page_size: int = Query(10, ge=1, le=100, description="Number of meals per page, default 10, max 100"),
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        meals, total = await get_paginated_meals_by_user(db, user_id, page, page_size)
        return PaginatedMeals(meals=meals, total=total, page=page, page_size=page_size)
    except MealCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except MealValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    

@router.get("/{meal_id}/detailed", response_model=dict)
async def get_detailed_meal_entry(
    meal_id: str,
    user_id: str = Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        return await get_detailed_meal(db, ObjectId(meal_id), user_id)
    except MealNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except MealCreationError as e:
        raise HTTPException(status_code=500, detail=str(e))