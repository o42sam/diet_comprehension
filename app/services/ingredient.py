from app.models.ingredient import Ingredient
from app.repositories.ingredient import create_ingredient as repo_create_ingredient, get_ingredients as repo_get_ingredients, search_ingredients as repo_search_ingredients
from app.exceptions.ingredient import IngredientCreationError, IngredientAlreadyExistsError, IngredientSearchError
from loguru import logger
from pymongo.errors import PyMongoError
from typing import List

async def create_ingredient(db, ingredient: Ingredient) -> Ingredient:
    try:
        ingredient_dict = ingredient.dict(exclude_unset=True)
        ingredient_id = await repo_create_ingredient(db, ingredient_dict)
        ingredient_dict["_id"] = ingredient_id
        ingredient_dict["id"] = str(ingredient_id)
        return Ingredient(**ingredient_dict)
    except IngredientAlreadyExistsError as e:
        raise
    except PyMongoError as e:
        logger.error(f"Database error while creating ingredient: {e}")
        raise IngredientCreationError(f"Failed to create ingredient due to a database error: {e}")

async def get_ingredients(db) -> List[Ingredient]:
    try:
        ingredients = await repo_get_ingredients(db)
        for ing in ingredients:
            ing["id"] = str(ing["_id"])
            del ing["_id"]
        return [Ingredient(**ing) for ing in ingredients]
    except PyMongoError as e:
        logger.error(f"Database error while fetching ingredients: {e}")
        raise IngredientCreationError(f"Failed to retrieve ingredients due to a database error: {e}")

async def search_ingredients(db, query: str) -> List[Ingredient]:
    logger.info(f"Searching ingredients with query: {query}")
    try:
        ingredients = await repo_search_ingredients(db, query)
        for ing in ingredients:
            ing["id"] = str(ing["_id"])
            del ing["_id"]
        return [Ingredient(**ing) for ing in ingredients]
    except PyMongoError as e:
        logger.error(f"Database error while searching ingredients: {e}")
        raise IngredientSearchError(f"Failed to search ingredients due to a database error: {e}")