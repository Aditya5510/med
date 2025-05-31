

import os
import motor.motor_asyncio
from pydantic_settings import BaseSettings
from typing import AsyncGenerator
from dotenv import load_dotenv

# Load environment variables from backend/.env
load_dotenv()

class Settings(BaseSettings):
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "health_planner_db")

    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "changeme_secret_key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings()


client: motor.motor_asyncio.AsyncIOMotorClient | None = None

async def get_database() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorDatabase, None]:
    """
    Dependency that yields a MongoDB database instance.
    The client is created on first access and reused thereafter.
    """
    global client
    if client is None:
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]
    try:
        yield db
    finally:
        
        pass
