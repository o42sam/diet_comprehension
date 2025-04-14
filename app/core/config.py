class Settings:
    MONGO_URI = "mongodb://localhost:27017"
    DB_NAME = "meal_tracker"
    REDIS_URL = "redis://localhost:6379"
    SECRET_KEY = "your-secret-key"  # Generate a secure key
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

settings = Settings()