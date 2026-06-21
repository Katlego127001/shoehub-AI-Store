from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.product import Product, Category, ProductImage
from app.schemas.product import ProductCreate

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_products(self):
        result = await self.db.execute(select(Product).options(selectinload(Product.images)))
        return result.scalars().all()

    async def get_product_by_id(self, product_id: int):
        result = await self.db.execute(
            select(Product).where(Product.id == product_id).options(selectinload(Product.images))
        )
        return result.scalar_one_or_none()

    async def get_products_by_category(self, category_name: str):
        result = await self.db.execute(
            select(Product).join(Category).where(Category.name == category_name).options(selectinload(Product.images))
        )
        return result.scalars().all()

    async def search_products(self, query: str):
        result = await self.db.execute(
            select(Product).where(
                (Product.name.ilike(f"%{query}%")) | 
                (Product.brand.ilike(f"%{query}%")) |
                (Product.description.ilike(f"%{query}%"))
            ).options(selectinload(Product.images))
        )
        return result.scalars().all()

    async def create_product(self, product_data: ProductCreate):
        db_product = Product(**product_data.model_dump())
        self.db.add(db_product)
        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product

    async def get_categories(self):
        result = await self.db.execute(select(Category))
        return result.scalars().all()
