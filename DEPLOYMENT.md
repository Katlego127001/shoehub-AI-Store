# ShoeHub AI Deployment Guide

## Environment Setup

1. Clone the repository.
2. Create a `.env` file from `.env.example`.
3. Fill in the following variables:
   - `TELEGRAM_TOKEN`: Get from @BotFather.
   - `OPENROUTER_API_KEY`: Get from OpenRouter.ai.
   - `STRIPE_SECRET_KEY`: Get from Stripe Dashboard.
   - `STRIPE_WEBHOOK_SECRET`: Get from Stripe CLI or Dashboard.

## Running with Docker

```bash
docker-compose up --build
```

## Manual Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run database migrations:
   ```bash
   alembic upgrade head
   ```
3. Run the API:
   ```bash
   uvicorn app.main:app --reload
   ```
4. Run the Bot:
   ```bash
   python -m app.bot.telegram_bot
   ```

## Production Considerations

- Use a production-grade database like AWS RDS or Managed PostgreSQL.
- Use a production WSGI/ASGI server like Gunicorn with Uvicorn workers.
- Set up SSL using Nginx or a load balancer.
- Configure S3-compatible storage for product images.
- Set up monitoring and logging (e.g., Sentry, Prometheus).
