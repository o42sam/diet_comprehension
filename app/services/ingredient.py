from app.models.ingredient import Ingredient, IngredientCreate
from app.repositories.ingredient import (
    create_ingredient as repo_create_ingredient,
    get_ingredients as repo_get_ingredients,
    search_ingredients as repo_search_ingredients
)
from app.exceptions.ingredient import (
    IngredientCreationError,
    IngredientAlreadyExistsError,
    IngredientSearchError,
    IngredientRetrievalError # Added
)
from loguru import logger
from pymongo.errors import PyMongoError
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List # Removed Dict
from bson import ObjectId # Import ObjectId

async def create_ingredient(db: AsyncIOMotorDatabase, ingredient_data: IngredientCreate) -> Ingredient:
    """
    Creates a new ingredient in the database.

    Args:
        db: The database connection.
        ingredient_data: The ingredient data to create (Pydantic model).

    Returns:
        The created Ingredient object.

    Raises:
        IngredientAlreadyExistsError: If the ingredient name already exists.
        IngredientCreationError: If a database error occurs during creation.
    """
    try:
        # Convert Pydantic model to dictionary for the repository layer
        ingredient_dict = ingredient_data.model_dump()
        logger.info(f"Attempting to create ingredient: {ingredient_dict.get('name')}")

        # Call repository to insert the ingredient data
        # Repository now returns ObjectId
        ingredient_id_obj = await repo_create_ingredient(db, ingredient_dict)
        logger.info(f"Ingredient created with ID: {ingredient_id_obj}")

        # Construct the full data for the Ingredient model, matching its fields
        created_ingredient_data = {
            **ingredient_dict,
            "_id": str(ingredient_id_obj) # Use '_id' alias and stringify the ObjectId
        }

        # Validate the complete data against the Ingredient model and return it
        # This ensures the returned object matches the API's response_model structure
        ingredient_model = Ingredient.model_validate(created_ingredient_data)
        return ingredient_model

    except IngredientAlreadyExistsError: # Catch specific repo error
        logger.warning(f"Ingredient creation failed: Name '{ingredient_data.name}' already exists.")
        raise # Re-raise the specific exception for the API layer to handle

    except PyMongoError as e:
        logger.error(f"Database error while creating ingredient '{ingredient_data.name}': {e}")
        raise IngredientCreationError(f"Failed to create ingredient '{ingredient_data.name}' due to a database error.")

    except Exception as e:
        logger.error(f"Unexpected error during ingredient creation: {e}")
        # Raise a generic creation error for unexpected issues
        raise IngredientCreationError(f"An unexpected error occurred while creating ingredient '{ingredient_data.name}'.")


async def get_ingredients(db: AsyncIOMotorDatabase) -> List[Ingredient]:
    """
    Retrieves all ingredients from the database.

    Args:
        db: The database connection.

    Returns:
        List of Ingredient objects.

    Raises:
        IngredientRetrievalError: If a database error occurs during retrieval.
    """
    try:
        logger.info("Fetching all ingredients")
        # Fetch the list of ingredient dictionaries from the repository
        ingredients_data = await repo_get_ingredients(db)
        logger.info(f"Retrieved {len(ingredients_data)} ingredients from repository")

        # Convert each dictionary to an Ingredient Pydantic model
        # model_validate handles the '_id' alias automatically
        ingredients = [Ingredient.model_validate(ing_data) for ing_data in ingredients_data]
        logger.info(f"Successfully validated {len(ingredients)} Ingredient models")
        return ingredients

    except PyMongoError as e:
        logger.error(f"Database error while fetching ingredients: {e}")
        raise IngredientRetrievalError(f"Failed to retrieve ingredients due to a database error: {e}")

    except Exception as e:
        logger.error(f"Unexpected error during ingredient retrieval: {e}")
        raise IngredientRetrievalError(f"An unexpected error occurred while retrieving ingredients.")


async def search_ingredients(db: AsyncIOMotorDatabase, query: str) -> List[Ingredient]:
    """
    Searches for ingredients by name matching the query (case-insensitive).

    Args:
        db: The database connection.
        query: The search query string.

    Returns:
        List of Ingredient objects matching the query.

    Raises:
        IngredientSearchError: If a database error occurs during search.
    """
    logger.info(f"Searching ingredients with query: '{query}'")
    try:
        # Fetch matching ingredient dictionaries from the repository
        ingredients_data = await repo_search_ingredients(db, query)
        logger.info(f"Found {len(ingredients_data)} ingredients matching query '{query}' in repository")

        # Convert each dictionary to an Ingredient Pydantic model
        ingredients = [Ingredient.model_validate(ing_data) for ing_data in ingredients_data]
        logger.info(f"Successfully validated {len(ingredients)} matching Ingredient models")
        return ingredients

    except PyMongoError as e:
        logger.error(f"Database error while searching ingredients for query '{query}': {e}")
        raise IngredientSearchError(f"Failed to search ingredients due to a database error: {e}")

    except Exception as e:
        logger.error(f"Unexpected error during ingredient search for query '{query}': {e}")
        raise IngredientSearchError(f"An unexpected error occurred while searching ingredients.")