"""
Eesti Keele Kursus — Telegram Bot
Telegram Stars payment + auto-add to channel
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

from telegram import Update, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

# === CONFIG ===
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "")  # e.g., @channel or -1001234567890
PRICE_STARS = int(os.environ.get("PRICE_STARS", 100))  # price in ⭐
COURSE_URL = "https://jamesdor.github.io/eesti-keele-kursus/"
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))  # your Telegram user ID for notifications

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
        f"💎 Доступ: {PRICE_STARS} ⭐ (Telegram Stars) — раз и навсегда\n\n"
        f"Чтобы купить доступ, нажми /buy"
    )


async def buy(update: Update, context: CallbackContext) -> None:
    """Send invoice for Telegram Stars payment."""
    chat_id = update.effective_chat.id
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) initiated purchase")

    await context.bot.send_invoice(
        chat_id=chat_id,
        title="Eesti keele kursus A1-C1",
        description=(
            "Полный доступ к курсу эстонского языка.\n"
            "• 27+ разделов материалов\n"
            "• Грамматика, лексика, аудио\n"
            "• Тесты и экзамены\n"
            "• Закрытый Telegram-канал\n"
            "• Все обновления бесплатно"
        ),
        payload="eesti_course_access",
        provider_token="",  # empty = Telegram Stars
        currency="XTR",
        prices=[LabeledPrice("Курс", PRICE_STARS)],
        need_name=False,
        need_phone=False,
        need_email=False,
        is_flexible=False,
    )


async def pre_checkout(update: Update, context: CallbackContext) -> None:
    """Answer pre-checkout (always accept)."""
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment(update: Update, context: CallbackContext) -> None:
    """Handle successful payment — add user to channel."""
    user = update.effective_user
    logger.info(f"Payment received from user {user.id} ({user.first_name})")

    channel_link = None
    if CHANNEL_ID:
        try:
            invite = await context.bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                member_limit=1,
            )
            channel_link = invite.invite_link
            logger.info(f"Invite link created for user {user.id}")
        except Exception as e:
            logger.error(f"Failed to create invite link: {e}")

    msg = (
        f"✅ Оплата получена! Спасибо, {user.first_name}!\n\n"
        f"📚 Ссылка на курс: {COURSE_URL}\n\n"
    )
    if channel_link:
        msg += (
            f"🔗 Ссылка для входа в канал (одноразовая):\n"
            f"{channel_link}\n\n"
        )
    msg += "Если возникнут вопросы — пишите."

    await update.message.reply_text(msg)

    # Notify admin
    if ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"💰 Новая продажа!\n"
                    f"Пользователь: {user.first_name} {user.last_name or ''}\n"
                    f"ID: {user.id}\n"
                    f"Username: @{user.username or 'нет'}\n"
                    f"Сумма: {PRICE_STARS} ⭐\n"
                    f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                ),
            )
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")


async def help_cmd(update: Update, context: CallbackContext) -> None:
    """Help message."""
    await update.message.reply_text(
        "/start — Приветствие\n"
        "/buy — Купить доступ к курсу\n"
        "/help — Помощь"
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
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_error_handler(error_handler)

    logger.info("Bot started polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
