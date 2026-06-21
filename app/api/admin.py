from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.product import Product, ProductCreate

router = APIRouter()

@router.get("/products", response_model=list[Product])
async def list_products(db: AsyncSession = Depends(get_db)):
    repo = ProductRepository(db)
    return await repo.get_all_products()

@router.post("/products", response_model=Product)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    repo = ProductRepository(db)
    return await repo.create_product(product)

# Add more admin routes here
