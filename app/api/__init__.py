from fastapi import APIRouter
from app.api import admin, payments

router = APIRouter()

router.include_router(admin.router, prefix="/admin", tags=["admin"])
router.include_router(payments.router, prefix="/payments", tags=["payments"])
