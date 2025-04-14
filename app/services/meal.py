from app.models.meal import Meal, MealListItem
from app.repositories.meal import create_meal, get_last_meal_by_user, get_meals_by_user_paginated
from app.exceptions.meal import MealCreationError, MealNotFoundError, MealValidationError
from loguru import logger
from datetime import datetime
from pymongo.errors import PyMongoError
from pydantic import ValidationError
from typing import Tuple, List
from app.constants import NUTRIENT_UNITS


async def create_meal_entry(db, meal: Meal, user_id: str) -> MealListItem:
    try:
        meal_dict = meal.dict(exclude_unset=True)
        meal_dict["user_id"] = user_id
        if not meal_dict.get("timestamp"):
            meal_dict["timestamp"] = datetime.utcnow()
        meal_id = await create_meal(db, meal_dict)
        meal_dict["_id"] = meal_id  # Use "_id" to match MongoDB's field
        meal_dict["id"] = str(meal_id)  # Convert ObjectId to string for Pydantic model
        return MealListItem(**meal_dict)
    except PyMongoError as e:
        logger.error(f"Database error while creating meal for user {user_id}: {e}")
        raise MealCreationError(f"Failed to create meal due to a database error: {e}")
    except ValidationError as e:
        logger.error(f"Validation error for meal data: {e}")
        raise MealValidationError(f"Invalid meal data: {e}")


async def get_last_meal_entry_by_user(db, user_id: str) -> MealListItem:
    try:
        meal = await get_last_meal_by_user(db, user_id)
        if not meal:
            raise MealNotFoundError(f"No meals found for user {user_id}")
        meal_out = MealListItem(**meal)
        logger.info(f"Last meal entry for user {user_id}: {meal_out.name}")
        return meal_out
    except PyMongoError as e:
        logger.error(f"Database error while fetching last meal for user {user_id}: {e}")
        raise MealCreationError(f"Failed to retrieve meal due to a database error: {e}")
    except ValidationError as e:
        logger.error(f"Validation error for meal data: {e}")
        raise MealValidationError(f"Invalid meal data retrieved: {e}")
    

async def get_paginated_meals_by_user(db, user_id: str, page: int = 1, page_size: int = 10) -> Tuple[List[MealListItem], int]:
    try:
        meals, total = await get_meals_by_user_paginated(db, user_id, page, page_size)
        meals_out = [MealListItem(**meal) for meal in meals]
        return meals_out, total
    except PyMongoError as e:
        logger.error(f"Database error while fetching meals for user {user_id}: {e}")
        raise MealCreationError(f"Failed to retrieve meals due to a database error: {e}")
    except ValidationError as e:
        logger.error(f"Validation error for meal data: {e}")
        raise MealValidationError(f"Invalid meal data retrieved: {e}")


async def get_detailed_meal(db, meal_id: str, user_id: str) -> dict:
    """Fetch a meal with detailed ingredient information, including nutrient units."""
    try:
        meal = await db.meals.find_one({"_id": meal_id, "user_id": user_id})
        if not meal:
            raise MealNotFoundError(f"Meal {meal_id} not found for user {user_id}")
        
        meal["_id"] = str(meal["_id"])
        
        detailed_ingredients = []
        for meal_ingredient in meal["ingredients"]:
            ingredient = await db.ingredients.find_one({"_id": meal_ingredient["ingredient_id"]})
            if ingredient:
                nutrients_with_units = {
                    nutrient: {"value": value, "unit": NUTRIENT_UNITS.get(nutrient, "unknown")}
                    for nutrient, value in ingredient["nutrients"].items()
                }
                detailed_ingredients.append({
                    "name": ingredient["name"],
                    "quantity": meal_ingredient["quantity"],
                    "nutrients": nutrients_with_units
                })
        
        meal["ingredients"] = detailed_ingredients
        return meal
    except PyMongoError as e:
        logger.error(f"Database error while fetching detailed meal {meal_id}: {e}")
        raise MealCreationError(f"Failed to retrieve meal due to a database error: {e}")