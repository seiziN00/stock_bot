"""Handler for /add command – add stock (entrada) via inline buttons.

Flow:
  1. /add  → show product buttons
  2. User taps a product → bot asks for quantity
  3. User types a number → bot registers the entrada
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

import sheets
from handlers.utils import escape_md

# Conversation states
CHOOSE_PRODUCT, ENTER_QUANTITY = range(2)

# Callback prefix
PREFIX = "add_"


async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show product buttons for adding stock."""
    productos = sheets.get_productos()

    keyboard = [
        [InlineKeyboardButton(p, callback_data=f"{PREFIX}{p}")]
        for p in productos
    ]
    await update.message.reply_text(
        "📥 *Añadir stock:* Selecciona un producto:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2",
    )
    return CHOOSE_PRODUCT


async def product_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the chosen product and ask for quantity."""
    query = update.callback_query
    await query.answer()

    producto = query.data.removeprefix(PREFIX)
    context.user_data["add_producto"] = producto

    await query.edit_message_text(
        f"Has seleccionado: *{escape_md(producto)}*\n¿Cuántas unidades quieres añadir?",
        parse_mode="MarkdownV2",
    )
    return ENTER_QUANTITY


async def quantity_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validate quantity and register the entrada."""
    try:
        cantidad = int(update.message.text)
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Ingresa un número entero positivo\\.", parse_mode="MarkdownV2")
        return ENTER_QUANTITY

    producto = context.user_data.pop("add_producto", None)
    if producto is None:
        await update.message.reply_text("❌ Sesión expirada\\. Usa /add para empezar de nuevo\\.", parse_mode="MarkdownV2")
        return ConversationHandler.END

    sheets.add_entrada(producto, cantidad)

    await update.message.reply_text(
        f"✅ Registrado: \\+{cantidad} unidades de *{escape_md(producto)}*\\.",
        parse_mode="MarkdownV2",
    )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current operation."""
    context.user_data.pop("add_producto", None)
    await update.message.reply_text("❌ Operación cancelada\\.", parse_mode="MarkdownV2")
    return ConversationHandler.END


def get_handlers() -> list:
    conv = ConversationHandler(
        entry_points=[CommandHandler("add", add_start)],
        states={
            CHOOSE_PRODUCT: [
                CallbackQueryHandler(product_chosen, pattern=f"^{PREFIX}"),
            ],
            ENTER_QUANTITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, quantity_entered),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("add", add_start),
            CommandHandler("venta", cancel),
            CommandHandler("stock", cancel),
            CommandHandler("poco", cancel),
        ],
        name="add_conversation",
        allow_reentry=True,
    )
    return [conv]
