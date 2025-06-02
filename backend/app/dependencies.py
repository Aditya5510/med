import os
import motor.motor_asyncio
from pydantic_settings import BaseSettings
from typing import AsyncGenerator
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    mongodb_uri: str
    database_name: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    hf_provider: str
    hf_api_token: str
    hf_model_name: str

    model_config = {"env_file": ".env"}

settings = Settings()

client: motor.motor_asyncio.AsyncIOMotorClient | None = None

async def get_database() -> AsyncGenerator[motor.motor_asyncio.AsyncIOMotorDatabase, None]:
    global client
    if client is None:
        client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.database_name]
    try:
        yield db
    finally:
        pass
