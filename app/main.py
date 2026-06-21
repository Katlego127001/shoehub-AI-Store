from fastapi import FastAPI
from app.api import router as api_router
from app.core.config import settings
from app.db import base  # Ensure all models are imported

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to ShoeHub AI API"}
