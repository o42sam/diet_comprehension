from app.models.user import UserCreate, UserOut
from app.repositories.user import create_user, get_user_by_username
from app.core.security import hash_password, verify_password, create_access_token
from fastapi import HTTPException
from loguru import logger

async def register_user(db, user: UserCreate) -> UserOut:
    hashed_password = hash_password(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    user_id = await create_user(db, user_dict)
    logger.info(f"User registered: {user.username}")
    return UserOut(id=user_id, username=user.username, email=user.email)

async def login_user(db, username: str, password: str) -> str:
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user["password"]):
        logger.warning(f"Login failed for username: {username}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user["_id"])})
    logger.info(f"User logged in: {username}")
    return token