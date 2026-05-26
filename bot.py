"""
Eesti Keele Kursus — Telegram Bot
Telegram Stars payment + auto-add to channel
"""

import os
import sys
import json
import logging

import httpx
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackContext,
)

# === CONFIG ===
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        logger.error(f"Config file not found: {CONFIG_FILE}")
        sys.exit(1)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg

config = load_config()
BOT_TOKEN = config.get("BOT_TOKEN", "")
CHANNEL_ID = config.get("CHANNEL_ID", "")
PRICE_STARS = int(config.get("PRICE_STARS", 100))
COURSE_URL = config.get("COURSE_URL", "https://jamesdor.github.io/eesti-keele-kursus/")
ADMIN_ID = int(config.get("ADMIN_ID", "0"))

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: CallbackContext) -> None:
    """Welcome message."""
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Tere, {user.first_name}!\n\n"
        f"Добро пожаловать на курс эстонского языка A1–C1.\n\n"
        f"📚 Материалы: грамматика, лексика, аудирование, тесты, экзамены\n"
        f"🎯 Уровни: от A1 до C1\n"
        f"💎 Доступ: 15€ — раз и навсегда\n\n"
        f"Чтобы купить доступ, нажми /buy"
    )


import httpx


async def buy(update: Update, context: CallbackContext) -> None:
    """Create Stripe Checkout session and send payment link."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    logger.info(f"User {user.id} ({user.first_name}) initiated purchase")

    # Get the Netlify function URL — try local config first, fallback to env
    netlify_url = config.get("NETLIFY_URL", "")
    checkout_api = f"{netlify_url}/create-checkout" if netlify_url else None

    if not checkout_api:
        await update.message.reply_text(
            "⚠️ Оплата временно недоступна. Напишите администратору."
        )
        logger.error("NETLIFY_URL not configured in config.json")
        return

    await update.message.reply_text("🔄 Создаю ссылку на оплату...")

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                checkout_api,
                json={
                    "telegram_id": user.id,
                    "first_name": user.first_name,
                },
            )
            data = resp.json()
    except Exception as e:
        logger.error(f"Failed to create checkout session: {e}")
        await update.message.reply_text(
            "❌ Не удалось создать ссылку на оплату. Попробуйте позже."
        )
        return

    if resp.status_code != 200 or not data.get("url"):
        logger.error(f"Checkout API error: {data}")
        await update.message.reply_text(
            "❌ Ошибка при создании оплаты. Попробуйте позже."
        )
        return

    await update.message.reply_text(
        f"💳 <b>Оплата курса Eesti keel A1-C1</b>\n\n"
        f"💰 Цена: 15€\n\n"
        f"👇 Нажмите на ссылку для оплаты:\n"
        f"{data['url']}\n\n"
        f"После успешной оплаты вы получите ссылку на Telegram-канал.",
        parse_mode="HTML",
    )


async def help_cmd(update: Update, context: CallbackContext) -> None:
    """Help message."""
    await update.message.reply_text(
        "/start — Приветствие\n"
        "/buy — Купить доступ к курсу\n"
        "/id — Мой Telegram ID\n"
        "/help — Помощь"
    )


async def show_id(update: Update, context: CallbackContext) -> None:
    """Show user their Telegram ID."""
    user = update.effective_user
    await update.message.reply_text(
        f"Твой Telegram ID: `{user.id}`\n\n"
        f"Вставь его в config.json в поле ADMIN_ID,\n"
        f"чтобы получать уведомления о продажах.",
        parse_mode="Markdown",
    )


async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors."""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set!")
        sys.exit(1)

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("id", show_id))
    app.add_handler(CommandHandler("buy", buy))
    app.add_error_handler(error_handler)

    logger.info("Bot started polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
