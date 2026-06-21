import httpx
from app.core.config import settings
import json

class AIService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = settings.OPENROUTER_MODEL

    async def _call_ai(self, messages, functions=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://shoehub.ai",
            "X-Title": "ShoeHub AI",
        }
        payload = {
            "model": self.model,
            "messages": messages,
        }
        if functions:
            payload["functions"] = functions
            payload["function_call"] = "auto"

        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()

    async def recommend_products(self, user_query: str, products_data: str):
        prompt = f"Based on the following user query: '{user_query}', and the available products: {products_data}, recommend the best shoes. Explain why."
        messages = [{"role": "system", "content": "You are a helpful shoe shopping assistant."}, {"role": "user", "content": prompt}]
        return await self._call_ai(messages)

    async def compare_products(self, products_to_compare: list):
        prompt = f"Compare these shoes: {json.dumps(products_to_compare)}. Detail their differences in price, features, and use cases."
        messages = [{"role": "system", "content": "You are a shoe expert."}, {"role": "user", "content": prompt}]
        return await self._call_ai(messages)

    async def answer_customer_question(self, question: str, context: str = ""):
        system_prompt = (
            "You are the ShoeHub AI assistant. You help users shop for shoes. "
            "You have access to the user's cart and order history. "
            "If the user wants to perform an action, you must include a command tag at the end of your response: "
            " - To checkout: [ACTION:CHECKOUT] "
            " - To view orders: [ACTION:ORDERS] "
            " - To browse: [ACTION:BROWSE] "
            " - To search: [ACTION:SEARCH:query] "
            "Always be polite and helpful."
        )
        messages = [
            {"role": "system", "content": system_prompt + "\nContext: " + context},
            {"role": "user", "content": question}
        ]
        return await self._call_ai(messages)

    async def suggest_related_products(self, product_id: int, product_details: str):
        prompt = f"Given this product: {product_details}, suggest 3 related or complementary products that a customer might want to buy."
        messages = [{"role": "system", "content": "You are a shopping assistant."}, {"role": "user", "content": prompt}]
        return await self._call_ai(messages)

    async def generate_product_description(self, product_name: str, features: list):
        prompt = f"Generate a compelling sales description for a shoe named '{product_name}' with these features: {', '.join(features)}."
        messages = [{"role": "system", "content": "You are a professional copywriter."}, {"role": "user", "content": prompt}]
        return await self._call_ai(messages)
