import uvicorn
from fastapi import FastAPI
from .dependencies import settings, client
from .routers import health, auth  

app = FastAPI(
    title="Personalized Health & Fitness Planner API",
    version="0.1.0"
)


app.include_router(auth.router)


app.include_router(health.router, prefix="/api/health", tags=["health"])

@app.on_event("startup")
async def startup_db_client():
    """
    Instantiates the Motor client (from dependencies.py) once at startup.
    """
    global client
    if client is None:
       
        from .dependencies import get_database
        async for _ in get_database():
            break
    print(f"✅ Connected to MongoDB at {settings.mongodb_uri}, DB: {settings.database_name}")

@app.on_event("shutdown")
async def shutdown_db_client():
    """
    Closes the global Motor client when the application shuts down.
    """
    global client
    if client:
        client.close()
        print("🛑 MongoDB client closed.")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
