"""Handlers for /start and /help commands."""

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

HELP_TEXT = (
    "🤖 *Comandos disponibles:*\n\n"
    "/add — Añadir stock \\(entrada\\)\n"
    "/venta — Registrar una venta \\(salida\\)\n"
    "/stock — Ver stock actual de todos los productos\n"
    "/poco — Ver productos con stock bajo \\(≤ 10\\)\n"
    "/help — Mostrar esta ayuda"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "¡Hola\\! Soy tu bot de inventario de marcianos 🍦\n\n" + HELP_TEXT,
        parse_mode="MarkdownV2",
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="MarkdownV2")


def get_handlers() -> list:
    return [
        CommandHandler("start", start),
        CommandHandler("help", help_cmd),
    ]
