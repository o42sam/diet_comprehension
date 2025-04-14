from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from app.core.config import settings
from fastapi import Depends

def get_mongo_client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.MONGO_URI)

def get_db(client: AsyncIOMotorClient = Depends(get_mongo_client)):
    return client[settings.DB_NAME]

# def get_redis_client() -> Redis:
#     return Redis.from_url(settings.REDIS_URL, decode_responses=True)