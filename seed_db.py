import asyncio
import os
from app.db.session import AsyncSessionLocal, engine
from app.db.base import Base
from app.models.product import Category, Product, ProductImage

async def seed():
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created.")

    async with AsyncSessionLocal() as db:
        # Create Categories
        cats = ["Running", "Sneakers", "Casual", "Formal"]
        category_objs = {}
        for cat_name in cats:
            c = Category(name=cat_name, description=f"The best {cat_name.lower()} shoes in the market.")
            db.add(c)
            await db.flush()
            category_objs[cat_name] = c
        
        # Data: (Name, Brand, Price, Category, ImagePath)
        shoe_data = [
            ("Nike Air Zoom Pegasus 40", "Nike", 2499.0, "Running", "images/running_shoes.jpg"),
            ("Adidas Ultraboost Light", "Adidas", 3299.0, "Running", "images/running_shoes.jpg"),
            ("Puma Suede Classic", "Puma", 1599.0, "Sneakers", "images/sneakers.jpg"),
            ("Vans Old Skool", "Vans", 1299.0, "Sneakers", "images/sneakers.jpg"),
            ("Clark's Desert Boot", "Clarks", 1899.0, "Casual", "images/casual_shoes.jpg"),
            ("Timberland Deck Shoes", "Timberland", 2100.0, "Casual", "images/casual_shoes.jpg"),
            ("Barker Oxford Black", "Barker", 4500.0, "Formal", "images/formal_shoes.jpg"),
            ("Hugo Boss Derby", "Hugo Boss", 3800.0, "Formal", "images/formal_shoes.jpg"),
        ]

        for name, brand, price, cat_name, img_path in shoe_data:
            p = Product(
                name=name,
                description=f"High quality {brand} {cat_name.lower()} shoes.",
                price=price,
                brand=brand,
                category_id=category_objs[cat_name].id,
                sizes=["7", "8", "9", "10", "11"],
                colors=["Black", "Brown", "Blue"],
                stock_quantity=15
            )
            db.add(p)
            await db.flush() # Get product ID
            
            img = ProductImage(product_id=p.id, url=img_path, is_primary=True)
            db.add(img)

        await db.commit()
        print("Database seeded with shoes for all categories and images!")

if __name__ == "__main__":
    asyncio.run(seed())
