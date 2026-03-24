"""Handlers for /stock and /poco commands."""

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

import sheets


async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current stock for every product."""
    stock_map = sheets.get_stock()

    if not stock_map:
        await update.message.reply_text("📦 No hay registros de stock aún\\.", parse_mode="MarkdownV2")
        return

    lines = [f"{prod} → {qty}" for prod, qty in stock_map.items()]
    text = "📦 *STOCK ACTUAL*\n```\n" + "\n".join(lines) + "\n```"

    await update.message.reply_text(text, parse_mode="MarkdownV2")


async def poco(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show products with stock ≤ threshold."""
    low = sheets.get_low_stock()

    if not low:
        await update.message.reply_text("✅ Todos los productos tienen stock suficiente\\.", parse_mode="MarkdownV2")
        return

    lines = [f"{prod} → {qty}" for prod, qty in low.items()]
    text = "⚠️ *STOCK BAJO \\(≤ 10\\)*\n```\n" + "\n".join(lines) + "\n```"

    await update.message.reply_text(text, parse_mode="MarkdownV2")


def get_handlers() -> list:
    return [
        CommandHandler("stock", stock),
        CommandHandler("poco", poco),
    ]
