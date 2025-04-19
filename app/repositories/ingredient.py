from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from app.exceptions.ingredient import IngredientAlreadyExistsError
from bson import ObjectId # Import ObjectId
from typing import List, Dict, Any # For type hints
from loguru import logger # Optional: for logging repo actions

async def create_ingredient(db: AsyncIOMotorDatabase, ingredient_data: Dict[str, Any]) -> ObjectId:
    """
    Inserts a new ingredient document into the database.

    Args:
        db: The database connection.
        ingredient_data: A dictionary representing the ingredient to insert.

    Returns:
        The ObjectId of the inserted document.

    Raises:
        IngredientAlreadyExistsError: If an ingredient with the same unique key (e.g., 'name') already exists.
        PyMongoError: For other database-related errors during insertion.
    """
    try:
        logger.debug(f"Inserting ingredient data: {ingredient_data.get('name')}")
        result = await db.ingredients.insert_one(ingredient_data)
        logger.debug(f"Insertion successful, ID: {result.inserted_id}")
        return result.inserted_id # Return the ObjectId directly
    except DuplicateKeyError:
        logger.warning(f"Duplicate key error for ingredient name: {ingredient_data.get('name')}")
        # Let the service layer catch and handle this specific error
        raise IngredientAlreadyExistsError(f"Ingredient with name '{ingredient_data.get('name')}' already exists")
    # Other PyMongoErrors will be caught by the service layer


async def get_ingredients(db: AsyncIOMotorDatabase) -> List[Dict[str, Any]]:
    """
    Retrieves all ingredient documents from the database.

    Args:
        db: The database connection.

    Returns:
        A list of dictionaries, each representing an ingredient document.

    Raises:
        PyMongoError: If a database error occurs during retrieval.
    """
    logger.debug("Finding all ingredients in repository")
    cursor = db.ingredients.find()
    # The service layer will handle potential PyMongoErrors here
    ingredients = await cursor.to_list(length=None) # Use None for potentially large lists cautiously
    logger.debug(f"Found {len(ingredients)} ingredients in repository")
    return ingredients

async def search_ingredients(db: AsyncIOMotorDatabase, query: str) -> List[Dict[str, Any]]:
    """
    Finds ingredient documents where the name matches the query (case-insensitive).

    Args:
        db: The database connection.
        query: The search string for the ingredient name.

    Returns:
        A list of dictionaries, each representing a matching ingredient document.

    Raises:
        PyMongoError: If a database error occurs during the search.
    """
    logger.debug(f"Searching ingredients in repository with query: '{query}'")
    # Use a case-insensitive regex search
    search_filter = {"name": {"$regex": query, "$options": "i"}}
    cursor = db.ingredients.find(search_filter)
    # The service layer will handle potential PyMongoErrors here
    ingredients = await cursor.to_list(length=None)
    logger.debug(f"Found {len(ingredients)} ingredients in repository matching query '{query}'")
    return ingredients