from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User, UserRole

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_user(self, telegram_id: str, full_name: str):
        result = await self.db.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                telegram_id=telegram_id,
                full_name=full_name,
                role=UserRole.CUSTOMER
            )
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
        return user
