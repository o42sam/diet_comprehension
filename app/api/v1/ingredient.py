from fastapi import APIRouter, Depends, HTTPException, status # Added status
from app.models.ingredient import Ingredient, IngredientCreate
from app.services.ingredient import ( # Import service functions
    create_ingredient,
    get_ingredients,
    search_ingredients
)
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.exceptions.ingredient import ( # Import specific exceptions
    IngredientCreationError,
    IngredientAlreadyExistsError,
    IngredientSearchError,
    IngredientRetrievalError # Added for get/search potentially
)
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase # Import db type hint

router = APIRouter(prefix="/ingredients", tags=["ingredients"])

@router.post(
    "/",
    response_model=Ingredient,
    status_code=status.HTTP_201_CREATED # Use 201 for creation
)
async def create_new_ingredient(
    ingredient: IngredientCreate,
    user_id: str = Depends(get_current_user), # Keep user_id if needed for audit/ownership later
    db: AsyncIOMotorDatabase = Depends(get_db) # Use specific type hint
):
    """
    Creates a new ingredient.
    """
    try:
        # Call the service layer function
        created_ingredient = await create_ingredient(db, ingredient)
        return created_ingredient
    except IngredientAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except IngredientCreationError as e:
        # Treat creation errors (like DB issues) as internal server errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")


@router.get("/", response_model=List[Ingredient])
async def list_ingredients(
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Retrieves a list of all ingredients.
    """
    try:
        # Call the service layer function
        return await get_ingredients(db)
    except IngredientRetrievalError as e: # Use a more specific exception if defined
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")

@router.get("/search", response_model=List[Ingredient])
async def search_ingredients_endpoint(
    query: str,
    user_id: str = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Searches for ingredients by name (case-insensitive).
    """
    if not query:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Search query cannot be empty")
    try:
        # Call the service layer function
        return await search_ingredients(db, query=query) # Pass query explicitly
    except IngredientSearchError as e:
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        # Catch unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An unexpected error occurred: {e}")