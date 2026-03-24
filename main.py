"""Stock Bot – Telegram bot for marciano inventory management.

Entry point: registers all handlers and starts polling.
"""

import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

import config
from handlers import start, stock, add, venta

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Reply to unrecognised commands."""
    await update.message.reply_text(
        "❓ Comando no reconocido. Usa /help para ver los comandos disponibles."
    )


def main() -> None:
    app = ApplicationBuilder().token(config.TELEGRAM_TOKEN).build()

    # Register handlers (order matters – ConversationHandlers first)
    for handler_module in (add, venta, start, stock):
        for h in handler_module.get_handlers():
            app.add_handler(h)

    # Fallback for unknown commands
    app.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    logger.info("Bot iniciado ✓")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
