from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.order_cart_payment import Order, OrderItem, OrderStatus

class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_order(self, user_id: int, total_amount: float, items: list):
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status=OrderStatus.PENDING
        )
        self.db.add(order)
        await self.db.flush()

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item['product_id'],
                quantity=item['quantity'],
                price_at_purchase=item['price'],
                size=item.get('size', 'N/A'),
                color=item.get('color', 'N/A')
            )
            self.db.add(order_item)
        
        await self.db.commit()
        await self.db.refresh(order)
        return order

    async def get_user_orders(self, user_id: int):
        result = await self.db.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()

    async def get_order_by_id(self, order_id: int):
        result = await self.db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()
