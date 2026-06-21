from fastapi import APIRouter, Request, Header, HTTPException, Depends
from app.services.stripe_service import StripeService
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
import stripe
from telegram import Bot
from app.core.config import settings
from app.models.order_cart_payment import Order, OrderStatus
from sqlalchemy.future import select

router = APIRouter()
stripe_service = StripeService()
telegram_bot = Bot(token=settings.TELEGRAM_TOKEN)

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    
    try:
        event = stripe_service.verify_webhook(payload, stripe_signature)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['metadata'].get('order_id')
        telegram_id = session['metadata'].get('telegram_id')
        
        # Update order status in DB
        if order_id and order_id != "999":
            result = await db.execute(select(Order).where(Order.id == int(order_id)))
            order = result.scalar_one_or_none()
            if order:
                order.status = OrderStatus.PAID
                await db.commit()
        
        # Notify the user via Telegram
        if telegram_id:
            try:
                await telegram_bot.send_message(
                    chat_id=telegram_id, 
                    text="✅ Payment Successful! Your order is now being processed. Thank you for shopping at ShoeHub AI! 👟"
                )
            except Exception as e:
                print(f"Failed to send Telegram notification: {e}")
                
    return {"status": "success"}
