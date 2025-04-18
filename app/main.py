from fastapi import FastAPI, Request
from fastapi_limiter import FastAPILimiter
# from app.dependencies.database import get_redis_client
from app.api.v1 import user, meal
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
from app.dependencies.database import get_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # redis = get_redis_client()
    # await FastAPILimiter.init(redis)
    db = await get_db()
    await db.ingredients.create_index("name", unique=True)
    logger.info("Application startup completed")
    yield
    
    # Shutdown
    # await FastAPILimiter.close()
    logger.info("Application shutdown completed")

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/")
async def root():
    return {"message": "Welcome to the Meal Tracker"}

app.include_router(user.router, prefix="/api/v1", tags=["User"])
app.include_router(meal.router, prefix="/api/v1", tags=["Meal"])

if (__name__ == "__main__"):
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)