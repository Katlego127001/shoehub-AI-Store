from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
from app.core.config import settings
from app.services.ai_service import AIService
from app.services.stripe_service import StripeService
from app.db.session import AsyncSessionLocal
from app.db import base # Ensure all models are imported for relationships
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.repositories.order_repository import OrderRepository
import logging
import json
import os

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

ai_service = AIService()
stripe_service = StripeService()

async def get_repos(db):
    return ProductRepository(db), UserRepository(db), OrderRepository(db)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    async with AsyncSessionLocal() as db:
        _, user_repo, _ = await get_repos(db)
        await user_repo.get_or_create_user(str(user.id), user.full_name)
    
    keyboard = [
        ["👟 Browse Shoes", "🔍 Search"],
        ["🛒 Cart", "📦 Orders"],
        ["🤖 AI Assistant", "ℹ️ FAQ"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"Welcome to ShoeHub AI, {user.first_name}! I'm your personal shoe expert. How can I help you today?",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Clean text for routing
    clean_text = text.replace("👟", "").replace("🔍", "").replace("🛒", "").replace("📦", "").replace("🤖", "").replace("ℹ️", "").strip().lower()
    
    if clean_text == "browse shoes" or clean_text == "browse":
        await browse_categories(update, context)
    elif clean_text == "search":
        context.user_data['mode'] = 'search'
        await update.message.reply_text("Just type what you're looking for (e.g., 'Nike running shoes')")
    elif clean_text == "cart" or clean_text == "view cart":
        await view_cart(update, context)
    elif clean_text == "orders" or clean_text == "view orders":
        await view_orders(update, context)
    elif clean_text == "ai assistant" or clean_text == "assistant":
        context.user_data['mode'] = 'ai'
        await update.message.reply_text("I'm listening! Ask me about sizes, styles, or recommendations.")
    elif clean_text == "checkout" or clean_text == "pay" or clean_text == "buy":
        await initiate_checkout_logic(update, context)
    elif clean_text == "faq":
        await update.message.reply_text("ShoeHub AI FAQ:\n1. Shipping: 3-5 days\n2. Returns: 30-day policy\n3. Payments: Secure via Stripe")
    else:
        mode = context.user_data.get('mode', 'ai')
        
        if mode == 'search':
            await update.message.reply_chat_action("typing")
            async with AsyncSessionLocal() as db:
                product_repo, _, _ = await get_repos(db)
                products = await product_repo.search_products(text)
                if not products:
                    await update.message.reply_text(f"No results found for '{text}'. Try another search?")
                else:
                    for product in products:
                        keyboard = [[InlineKeyboardButton("Add to Cart", callback_data=f"add_{product.id}")]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        caption = f"🔎 Found: {product.name}\nBrand: {product.brand}\nPrice: R{product.price}"
                        
                        image = next((img.url for img in product.images if img.is_primary), None)
                        if image and os.path.exists(image):
                            await update.message.reply_photo(photo=open(image, 'rb'), caption=caption, reply_markup=reply_markup)
                        else:
                            await update.message.reply_text(caption, reply_markup=reply_markup)
            context.user_data['mode'] = None # Reset mode
        else:
            # AI Assistant with DB, Order, and Cart context
            await update.message.reply_chat_action("typing")
            async with AsyncSessionLocal() as db:
                product_repo, user_repo, order_repo = await get_repos(db)
                
                # Context: Products
                products = await product_repo.get_all_products()
                products_context = [{"name": p.name, "price": p.price, "brand": p.brand} for p in products[:10]]
                
                # Context: User Orders
                user = await user_repo.get_or_create_user(str(update.effective_user.id), update.effective_user.full_name)
                orders = await order_repo.get_user_orders(user.id)
                orders_context = []
                for o in orders[:5]:
                    items = [{"name": item.product.name, "qty": item.quantity} for item in o.items]
                    orders_context.append({
                        "order_id": o.id, 
                        "status": o.status.value, 
                        "total": o.total_amount, 
                        "date": str(o.created_at),
                        "items": items
                    })

                # Context: Current Cart
                cart = context.user_data.get('cart', {})
                cart_items = []
                cart_total = 0
                for pid, qty in cart.items():
                    product = await product_repo.get_product_by_id(pid)
                    if product:
                        subtotal = product.price * qty
                        cart_total += subtotal
                        cart_items.append({"name": product.name, "quantity": qty, "price": product.price, "subtotal": subtotal})
                
                cart_context = {"items": cart_items, "total": cart_total}
                
                full_context = (
                    f"Available Products: {json.dumps(products_context)}\n"
                    f"User Orders: {json.dumps(orders_context)}\n"
                    f"User Current Cart: {json.dumps(cart_context)}"
                )
                
                response = await ai_service.answer_customer_question(text, context=full_context)
                ai_text = response['choices'][0]['message']['content']
                
                # Handle AI commands/actions
                if "[ACTION:CHECKOUT]" in ai_text:
                    ai_text = ai_text.replace("[ACTION:CHECKOUT]", "").strip()
                    await update.message.reply_text(ai_text)
                    await initiate_checkout_logic(update, context)
                    return
                elif "[ACTION:ORDERS]" in ai_text:
                    ai_text = ai_text.replace("[ACTION:ORDERS]", "").strip()
                    await update.message.reply_text(ai_text)
                    await view_orders(update, context)
                    return
                elif "[ACTION:BROWSE]" in ai_text:
                    ai_text = ai_text.replace("[ACTION:BROWSE]", "").strip()
                    await update.message.reply_text(ai_text)
                    await browse_categories(update, context)
                    return
                
                await update.message.reply_text(ai_text)

async def browse_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = ["Running", "Sneakers", "Casual", "Formal"] # Simplified for demo
    keyboard = [[InlineKeyboardButton(cat, callback_data=f"cat_{cat}")] for cat in categories]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Select a category:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("cat_"):
        category_name = data.split("_")[1]
        async with AsyncSessionLocal() as db:
            product_repo, _, _ = await get_repos(db)
            products = await product_repo.get_products_by_category(category_name)
            
            if not products:
                await query.edit_message_text(f"No shoes found in {category_name} yet. Check back soon!")
                return
            
            for product in products:
                keyboard = [[InlineKeyboardButton("Add to Cart", callback_data=f"add_{product.id}")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                caption = f"👟 {product.name}\nBrand: {product.brand}\nPrice: R{product.price}\n{product.description}"
                
                image = next((img.url for img in product.images if img.is_primary), None)
                if image and os.path.exists(image):
                    await query.message.reply_photo(photo=open(image, 'rb'), caption=caption, reply_markup=reply_markup)
                else:
                    await query.message.reply_text(caption, reply_markup=reply_markup)
    
    elif data.startswith("add_"):
        product_id = int(data.split("_")[1])
        cart = context.user_data.get('cart', {})
        cart[product_id] = cart.get(product_id, 0) + 1
        context.user_data['cart'] = cart
        await query.message.reply_text("Added to cart! Type '🛒 Cart' to view.")

async def view_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get('cart', {})
    if not cart:
        await update.message.reply_text("Your cart is empty.")
        return
    
    summary = "Your Cart:\n"
    total = 0
    
    async with AsyncSessionLocal() as db:
        product_repo, _, _ = await get_repos(db)
        for pid, qty in cart.items():
            product = await product_repo.get_product_by_id(pid)
            if product:
                subtotal = product.price * qty
                total += subtotal
                summary += f"- {product.name} x{qty}: R{subtotal}\n"
    
    summary += f"\nTotal: R{total}"
    
    keyboard = [
        [InlineKeyboardButton("💳 Checkout (Stripe)", callback_data="checkout")],
        [InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(summary, reply_markup=reply_markup)

async def handle_clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['cart'] = {}
    await query.edit_message_text("Cart cleared.")

async def view_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    async with AsyncSessionLocal() as db:
        _, user_repo, order_repo = await get_repos(db)
        user = await user_repo.get_or_create_user(telegram_id, update.effective_user.full_name)
        orders = await order_repo.get_user_orders(user.id)
        
        if not orders:
            await update.message.reply_text("You have no active orders. Time to shop! 👟")
            return
        
        message = "📦 Your Order History:\n\n"
        for order in orders:
            status_emoji = "⏳" if order.status.value == "pending" else "✅" if order.status.value == "paid" else "🚚"
            message += f"{status_emoji} Order #{order.id}\n"
            message += f"📅 Date: {order.created_at.strftime('%Y-%m-%d')}\n"
            message += f"💰 Total: R{order.total_amount}\n"
            message += f"📍 Status: {order.status.value.capitalize()}\n"
            message += "-------------------\n"
        
        await update.message.reply_text(message)

async def handle_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await initiate_checkout_logic(update, context)

async def initiate_checkout_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cart = context.user_data.get('cart', {})
    user_obj = update.effective_user
    
    # If called from a callback query, the user_obj is in callback_query
    if not user_obj and update.callback_query:
        user_obj = update.callback_query.from_user

    if not cart:
        msg = "Cart is empty."
        if update.callback_query:
            await update.callback_query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
        return

    items_for_stripe = []
    items_for_db = []
    total_amount = 0
    
    async with AsyncSessionLocal() as db:
        product_repo, user_repo, order_repo = await get_repos(db)
        user = await user_repo.get_or_create_user(str(user_obj.id), user_obj.full_name)
        
        for pid, qty in cart.items():
            product = await product_repo.get_product_by_id(pid)
            if product:
                subtotal = product.price * qty
                total_amount += subtotal
                items_for_stripe.append({"name": product.name, "price": product.price, "quantity": qty})
                items_for_db.append({
                    "product_id": product.id,
                    "quantity": qty,
                    "price": product.price
                })

        # Create real order in DB
        order = await order_repo.create_order(user.id, total_amount, items_for_db)

    try:
        bot_info = await context.bot.get_me()
        bot_username = bot_info.username
        
        session = await stripe_service.create_checkout_session(
            order_id=order.id,
            items=items_for_stripe,
            success_url=f"https://t.me/{bot_username}", 
            cancel_url=f"https://t.me/{bot_username}",
            metadata={
                "order_id": str(order.id),
                "telegram_id": str(user_obj.id)
            }
        )
        msg = f"Ready to pay? Use this secure Stripe link: {session.url}"
        if update.callback_query:
            await update.callback_query.message.reply_text(msg)
        else:
            await update.message.reply_text(msg)
            
        context.user_data['cart'] = {}
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        error_msg = "Sorry, there was an error initiating checkout."
        if update.callback_query:
            await update.callback_query.message.reply_text(error_msg)
        else:
            await update.message.reply_text(error_msg)

async def admin_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("--- Admin Dashboard ---\n1. Revenue: R54,000\n2. Orders: 12 Pending\n3. Inventory: 4 Low Stock Items")

def run_bot():
    app = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_dashboard))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern="^(cat_|add_)"))
    app.add_handler(CallbackQueryHandler(handle_checkout, pattern="^checkout$"))
    app.add_handler(CallbackQueryHandler(handle_clear_cart, pattern="^clear_cart$"))
    
    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
