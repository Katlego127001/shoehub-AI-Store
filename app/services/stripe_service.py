import stripe
import asyncio
from app.core.config import settings
from typing import List, Dict

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    def __init__(self):
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    async def create_checkout_session(self, order_id: int, items: List[Dict], success_url: str, cancel_url: str, customer_email: str = None, metadata: Dict = None):
        """
        items format: [{"name": "Shoe Name", "price": 100.0, "quantity": 1}]
        """
        line_items = []
        for item in items:
            line_items.append({
                'price_data': {
                    'currency': 'zar',
                    'product_data': {
                        'name': item['name'],
                    },
                    'unit_amount': int(item['price'] * 100),
                },
                'quantity': item['quantity'],
            })

        # Run synchronous stripe call in a separate thread
        session = await asyncio.to_thread(
            stripe.checkout.Session.create,
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email, # Will be None if not provided, making it editable on Stripe page
            metadata=metadata or {'order_id': order_id}
        )
        return session

    def verify_webhook(self, payload: str, sig_header: str):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, self.webhook_secret
            )
            return event
        except ValueError:
            # Invalid payload
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError:
            # Invalid signature
            raise Exception("Invalid signature")
