from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..dependencies import get_database

router = APIRouter()

@router.get("/ping")
async def ping(db: AsyncIOMotorDatabase = Depends(get_database)):
    collections = await db.list_collection_names()
    return {"status": "alive", "collections": collections}
