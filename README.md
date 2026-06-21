# 👟 ShoeHub AI: Production-Ready Telegram AI Shoe Store

ShoeHub AI is a complete, end-to-end conversational commerce platform. It combines the power of **FastAPI**, **Telegram Bots**, **OpenRouter (LLMs)**, and **Stripe** to create a seamless shopping experience where the AI doesn't just talk—it sells.

---

## 🌟 Key Features

### 🤖 Agentic AI Shopping Assistant
*   **Conversational Discovery**: Find shoes through natural language (e.g., "I need red running shoes under R2000").
*   **Context-Aware**: The AI knows your **Current Cart** and **Order History**.
*   **Action-Oriented**: The AI can trigger bot functions like opening the checkout, browsing categories, or searching.
*   **Expert Advice**: Provides sizing guidance and compares different models.

### 💳 Seamless Payments & Orders
*   **Stripe Integration**: Secure checkout sessions with editable customer information.
*   **Order Tracking**: Persistent order history in PostgreSQL with real-time status updates (Pending -> Paid).
*   **Webhook Sync**: Automatic order status updates via Stripe Webhooks and instant Telegram notifications.

### 👟 Premium Catalog Management
*   **Image Support**: High-quality product photography sent directly in-chat.
*   **Category Browsing**: Visual exploration of Running, Sneakers, Casual, and Formal collections.
*   **Inventory Tracking**: Managed stock quantities and brand filtering.

### 🛡️ Production-Grade Architecture
*   **Clean Architecture**: Separation of concerns with Repositories, Services, and Models.
*   **Asynchronous Core**: Built on `FastAPI` and `SQLAlchemy` (AsyncPG) for high performance.
*   **Dockerized**: Full containerization for API, Bot, DB, and Redis.

---

## 🏗️ Tech Stack

-   **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0
-   **Database**: PostgreSQL 15, Redis 7
-   **Bot Framework**: python-telegram-bot v21+
-   **Payments**: Stripe API
-   **AI**: OpenRouter (GPT-3.5/GPT-4 models)
-   **DevOps**: Docker, Docker Compose

---

## 🚀 Quick Start

### 1. Prerequisites
-   Docker & Docker Compose
-   Telegram Bot Token (from [@BotFather](https://t.me/botfather))
-   OpenRouter API Key
-   Stripe Secret Key

### 2. Environment Setup
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

### 3. Launch
```bash
docker-compose up --build
```

### 4. Seed Data
Populate your store with premium shoes and images:
```bash
docker-compose exec api python -m seed_db
```

---

## 🛠️ Project Structure

```text
shoehub-ai/
├── app/
│   ├── api/          # FastAPI routes (Webhooks, Admin)
│   ├── bot/          # Telegram Bot Handlers & Logic
│   ├── core/         # Settings & Config
│   ├── db/           # Session & Base Models
│   ├── models/       # SQLAlchemy ORM Entities
│   ├── repositories/ # Data Access Layer
│   ├── services/     # AI & Payment Integrations
│   └── schemas/      # Pydantic Validation
├── images/           # Generated Product Assets
├── Dockerfile        # Container Config
└── seed_db.py        # Database Initialization Script
```

---

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License
MIT License. Created for Arena.ai Agent Mode demonstration.
