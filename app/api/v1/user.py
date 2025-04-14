from fastapi import APIRouter, Depends, HTTPException
from app.models.user import UserCreate, UserLogin, UserOut
from app.services.user import register_user, login_user
from app.dependencies.database import get_db
# from  fastapi_limiter.depends import RateLimiter
from app.core.logger import logger

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserOut) # ADD RATE LIMITING WHEN REDIS IS UP: dependencies=[Depends(RateLimiter(times=10, seconds=60))]
async def register(user: UserCreate, db = Depends(get_db)):
    logger.info(f"Registering user: {user.username}")
    return await register_user(db, user)

@router.post("/login")
async def login(user: UserLogin, db = Depends(get_db)):
    token = await login_user(db, user.username, user.password)
    return {"access_token": token, "token_type": "bearer"}