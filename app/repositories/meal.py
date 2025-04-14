from motor.motor_asyncio import AsyncIOMotorDatabase

async def create_meal(db: AsyncIOMotorDatabase, meal_data: dict) -> str:
    result = await db.meals.insert_one(meal_data)
    return str(result.inserted_id)

async def get_meals_by_user(db: AsyncIOMotorDatabase, user_id: str) -> list:
    cursor = db.meals.find({"user_id": user_id})
    return await cursor.to_list(length=None)

async def get_last_meal_by_user(db: AsyncIOMotorDatabase, user_id: str) -> dict | None:
    cursor = db.meals.find({"user_id": user_id}).sort("timestamp", -1).limit(1)
    meal_list = await cursor.to_list(length=1)
    if not meal_list:
        return None
    meal = meal_list[0]
    meal['_id'] = str(meal['_id'])
    return meal

async def get_meals_by_user_paginated(db: AsyncIOMotorDatabase, user_id: str, page: int, page_size: int) -> tuple[list, int]:
    skip = (page - 1) * page_size
    cursor = db.meals.find({"user_id": user_id}).skip(skip).limit(page_size)
    meals = await cursor.to_list(length=page_size)
    for meal in meals:
        meal['_id'] = str(meal['_id'])  # Convert ObjectId to string for consistency
    total = await db.meals.count_documents({"user_id": user_id})
    return meals, total