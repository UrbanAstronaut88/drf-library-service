import os
import logging
import requests
from borrowings.models import Borrowing
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_telegram_message(message: str) -> bool:
    """Send message to telegram chat. Returns True if success, False otherwise."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram bot token or chat_id not set")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            return True
        else:
            logger.error("Error sending message in Telegram: %s", response.text)
            return False
    except requests.RequestException as e:
        logger.error("Exception while sending Telegram message: %s", str(e))
        return False


def format_borrowing_message(borrowing: Borrowing) -> str:
    """Creates a message about a new booking."""
    return (
        "📚 <b>New reservation!</b>\n"
        f"👤 User: {borrowing.user.first_name} {borrowing.user.last_name}\n"
        f"📖 Book: {borrowing.book.title}\n"
        f"📅 Start date: {borrowing.borrow_date}\n"
        f"📅 Return date: {borrowing.expected_return_date}"
    )


def send_borrowing_notification(borrowing: Borrowing) -> bool:
    """Generates a booking message and sends it to Telegram."""
    message = format_borrowing_message(borrowing)
    return send_telegram_message(message)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler for /start command."""
    await update.message.reply_text("Hello! I'm your library bot.")


def start_polling_bot():
    """Starts a simple Telegram bot that responds to /start command."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram bot token not set")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    logger.info("Telegram bot started. Polling...")
    app.run_polling()
