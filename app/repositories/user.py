from motor.motor_asyncio import AsyncIOMotorDatabase

async def create_user(db: AsyncIOMotorDatabase, user_data: dict) -> str:
    result = await db.users.insert_one(user_data)
    return str(result.inserted_id)

async def get_user_by_username(db: AsyncIOMotorDatabase, username: str) -> dict:
    return await db.users.find_one({"username": username})