"""
Eesti Keele Kursus — Telegram Bot
Telegram Stars payment + auto-add to channel
"""

import os
import sys
import json
import logging

from telegram import Update, LabeledPrice
from telegram.ext import (
    Application,
    CommandHandler,
    PreCheckoutQueryHandler,
    MessageHandler,
    filters,
    CallbackContext,
)

LOG_FILE = os.path.join(os.path.dirname(__file__), "bot_runtime.log")
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# === CONFIG ===
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        logger.warning(f"Config file not found: {CONFIG_FILE}; using environment variables")
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)

def get_setting(name, default=""):
    value = os.getenv(name)
    if value not in (None, ""):
        return value
    return config.get(name, default)

config = load_config()
BOT_TOKEN = get_setting("BOT_TOKEN")
BOT_USERNAME = get_setting("BOT_USERNAME", "eesti_keele_kursus_bot")
CHANNEL_ID = get_setting("CHANNEL_ID")
COURSE_URL = get_setting("COURSE_URL", "https://jamesdor.github.io/eesti-keele-kursus/")
ADMIN_ID = int(get_setting("ADMIN_ID", "0") or "0")
COURSE_FILE = get_setting("COURSE_FILE")
STARS_PRICE = int(os.getenv("STARS_PRICE") or os.getenv("PRICE_STARS") or config.get("STARS_PRICE", 2000))


async def send_invite_link(context: CallbackContext, user_id: int) -> str | None:
    """Create one-time invite link to the channel."""
    if not CHANNEL_ID:
        return None
    try:
        invite = await context.bot.create_chat_invite_link(
            chat_id=CHANNEL_ID,
            member_limit=1,
        )
        return invite.invite_link
    except Exception as e:
        logger.error(f"Failed to create invite link: {e}")
        return None


async def _grant_access(context: CallbackContext, user, order_id: str) -> None:
    """Send invite link + course URL + watermarked course file + notify admin."""
    invite_link = await send_invite_link(context, user.id)

    msg = (
        f"✅ Оплата получена! Спасибо, {user.first_name}!\n\n"
        f"📚 Ссылка на курс: {COURSE_URL}\n\n"
    )
    if invite_link:
        msg += (
            f"🔗 Ссылка для входа в канал (одноразовая):\n"
            f"{invite_link}\n\n"
        )
    msg += "Сейчас пришлю файл курса с вашей личной подписью."
    await context.bot.send_message(chat_id=user.id, text=msg)

    # Send watermarked course file
    if COURSE_FILE and os.path.exists(COURSE_FILE):
        try:
            watermark = (
                f'<div style="position:fixed;bottom:0;left:0;right:0;'
                f'background:#222;color:#ffcc00;text-align:center;'
                f'padding:4px 8px;font-size:9pt;z-index:99999;'
                f'font-family:Arial,sans-serif;">'
                f'@{user.username or "user"} | ID: {user.id} | '
                f'Курс Eesti keel A1-C1 &copy; 2026'
                f'</div>'
            )
            with open(COURSE_FILE, "r", encoding="utf-8") as f:
                html = f.read()
            watermarked = html.replace("</body>", f"{watermark}\n</body>")

            import tempfile
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", encoding="utf-8", delete=False
            )
            tmp.write(watermarked)
            tmp.close()

            with open(tmp.name, "rb") as fh:
                await context.bot.send_document(
                    chat_id=user.id,
                    document=fh,
                    filename="Eesti_keele_kursus.html",
                )

            os.unlink(tmp.name)
        except Exception as e:
            logger.error(f"Failed to send watermarked file: {e}")
            await context.bot.send_message(
                chat_id=user.id,
                text="❌ Не удалось отправить файл курса. Напишите администратору.",
            )
    else:
        logger.warning("COURSE_FILE not configured or not found")

    # Notify admin
    if ADMIN_ID:
        try:
            admin_msg = (
                f"💰 Новая продажа!\n"
                f"Пользователь: {user.first_name} {user.last_name or ''}\n"
                f"ID: {user.id}\n"
                f"Username: @{user.username or 'нет'}\n"
                f"Order: {order_id}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")


async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"👋 Tere, {user.first_name}!\n\n"
        f"Добро пожаловать на курс эстонского языка A1–C1.\n\n"
        f"📚 Материалы: грамматика, лексика, аудирование, тесты, экзамены\n"
        f"🎯 Уровни: от A1 до C1\n"
        f"💎 Доступ: {STARS_PRICE} Telegram Stars — раз и навсегда\n\n"
        f"Чтобы купить доступ, нажми /buy"
    )


async def buy(update: Update, context: CallbackContext) -> None:
    """Send Telegram Stars invoice."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) initiated purchase")

    await context.bot.send_invoice(
        chat_id=user.id,
        title="Eesti keele kursus A1-C1",
        description="Полный доступ ко всем материалам курса эстонского языка. Грамматика, лексика, аудирование, тесты, экзамены A1-C1.",
        payload="course_access",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(label="Курс Eesti keel A1-C1", amount=STARS_PRICE)],
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


async def pre_checkout(update: Update, context: CallbackContext) -> None:
    """Answer pre-checkout query (always approve)."""
    query = update.pre_checkout_query
    if query.invoice_payload != "course_access":
        await query.answer(ok=False, error_message="Неверный платёж. Начните заново: /buy")
        return
    await query.answer(ok=True)


async def payment_success(update: Update, context: CallbackContext) -> None:
    """Handle successful Telegram Stars payment."""
    user = update.effective_user
    payment = update.message.successful_payment
    stars_amount = payment.total_amount
    charge_id = payment.telegram_payment_charge_id
    logger.info(f"Payment success: user {user.id}, Stars: {stars_amount}, charge: {charge_id}")

    await _grant_access(context, user, charge_id)


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
    app.add_handler(PreCheckoutQueryHandler(pre_checkout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, payment_success))
    app.add_error_handler(error_handler)

    logger.info("Bot started polling...")
    app.run_polling()


if __name__ == "__main__":
    main()
