from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from app.exceptions.ingredient import IngredientAlreadyExistsError

async def create_ingredient(db: AsyncIOMotorDatabase, ingredient_data: dict) -> str:
    try:
        result = await db.ingredients.insert_one(ingredient_data)
        return str(result.inserted_id)
    except DuplicateKeyError:
        raise IngredientAlreadyExistsError(f"Ingredient with name '{ingredient_data['name']}' already exists")

async def get_ingredients(db: AsyncIOMotorDatabase) -> list:
    cursor = db.ingredients.find()
    return await cursor.to_list(length=None)

async def search_ingredients(db: AsyncIOMotorDatabase, query: str) -> list:
    cursor = db.ingredients.find({"name": {"$regex": query, "$options": "i"}})
    return await cursor.to_list(length=None)