"""Handler for /venta command – register a sale (salida) via inline buttons.

Flow:
  1. /venta → show product toggle buttons + ✅ Confirmar
  2. User taps products to toggle selection (✓/✗ visual feedback)
  3. User taps ✅ Confirmar → bot asks quantity for each selected product one by one
  4. After all quantities entered → register all salidas and show summary
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
SELECT_PRODUCTS, ENTER_QUANTITIES = range(2)

# Callback prefixes
TOGGLE = "vtoggle_"
CONFIRM = "vconfirm"

_VENTA_KEYS = ("venta_productos_list", "venta_selected", "venta_pending", "venta_items")


def _cleanup(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove all venta-related keys from user_data."""
    for key in _VENTA_KEYS:
        context.user_data.pop(key, None)


def _build_keyboard(productos: list[str], selected: set[str]) -> InlineKeyboardMarkup:
    """Build the product-selection keyboard with toggle indicators."""
    keyboard = []
    for p in productos:
        mark = "✅" if p in selected else "⬜"
        keyboard.append([InlineKeyboardButton(f"{mark} {p}", callback_data=f"{TOGGLE}{p}")])
    keyboard.append([InlineKeyboardButton("✅ Confirmar selección", callback_data=CONFIRM)])
    return InlineKeyboardMarkup(keyboard)


async def venta_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show product toggle buttons."""
    productos = sheets.get_productos()
    context.user_data["venta_productos_list"] = productos
    context.user_data["venta_selected"] = set()

    await update.message.reply_text(
        "🛒 *Venta:* Selecciona los productos vendidos y luego confirma:",
        reply_markup=_build_keyboard(productos, set()),
        parse_mode="MarkdownV2",
    )
    return SELECT_PRODUCTS


async def toggle_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Toggle a product in/out of the selection."""
    query = update.callback_query
    await query.answer()

    producto = query.data.removeprefix(TOGGLE)
    selected: set[str] = context.user_data.get("venta_selected", set())

    if producto in selected:
        selected.discard(producto)
    else:
        selected.add(producto)

    context.user_data["venta_selected"] = selected
    productos = context.user_data["venta_productos_list"]

    await query.edit_message_reply_markup(
        reply_markup=_build_keyboard(productos, selected),
    )
    return SELECT_PRODUCTS


async def confirm_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Lock in the selection and start asking quantities one by one."""
    query = update.callback_query
    await query.answer()

    selected: set[str] = context.user_data.get("venta_selected", set())
    if not selected:
        await query.answer("⚠️ No seleccionaste ningún producto.", show_alert=True)
        return SELECT_PRODUCTS

    # Prepare the quantity-collection queue
    pending = list(selected)
    context.user_data["venta_pending"] = pending
    context.user_data["venta_items"] = []  # [(producto, cantidad), ...]

    first = pending[0]
    await query.edit_message_text(
        f"¿Cuántas unidades de *{escape_md(first)}* se vendieron?",
        parse_mode="MarkdownV2",
    )
    return ENTER_QUANTITIES


async def quantity_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Collect quantity for the current product, then move to the next or finish."""
    pending: list[str] | None = context.user_data.get("venta_pending")
    if not pending:
        _cleanup(context)
        await update.message.reply_text(
            "❌ Sesión expirada\\. Usa /venta para empezar de nuevo\\.",
            parse_mode="MarkdownV2",
        )
        return ConversationHandler.END

    try:
        cantidad = int(update.message.text)
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("❌ Ingresa un número entero positivo\\.", parse_mode="MarkdownV2")
        return ENTER_QUANTITIES

    items: list[tuple[str, int]] = context.user_data.get("venta_items", [])
    current_product = pending.pop(0)

    # Validate stock
    stock_map = sheets.get_stock()
    available = stock_map.get(current_product, 0)
    if available < cantidad:
        # Put it back and ask again
        pending.insert(0, current_product)
        await update.message.reply_text(
            f"❌ Stock insuficiente de *{escape_md(current_product)}*\\.\n"
            f"Disponible: {available}\\. Intenta de nuevo:",
            parse_mode="MarkdownV2",
        )
        return ENTER_QUANTITIES

    items.append((current_product, cantidad))
    context.user_data["venta_items"] = items

    if pending:
        next_product = pending[0]
        await update.message.reply_text(
            f"¿Cuántas unidades de *{escape_md(next_product)}* se vendieron?",
            parse_mode="MarkdownV2",
        )
        return ENTER_QUANTITIES

    # All quantities collected – register the sale
    sheets.add_salidas(items)

    lines = [f"• {qty} {escape_md(prod)}" for prod, qty in items]
    summary = "📈 *Venta registrada:*\n" + "\n".join(lines)

    await update.message.reply_text(summary, parse_mode="MarkdownV2")
    _cleanup(context)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current sale."""
    _cleanup(context)
    await update.message.reply_text("❌ Venta cancelada\\.", parse_mode="MarkdownV2")
    return ConversationHandler.END


def get_handlers() -> list:
    conv = ConversationHandler(
        entry_points=[CommandHandler("venta", venta_start)],
        states={
            SELECT_PRODUCTS: [
                CallbackQueryHandler(toggle_product, pattern=f"^{TOGGLE}"),
                CallbackQueryHandler(confirm_selection, pattern=f"^{CONFIRM}$"),
            ],
            ENTER_QUANTITIES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, quantity_entered),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("venta", venta_start),
            CommandHandler("add", cancel),
            CommandHandler("stock", cancel),
            CommandHandler("poco", cancel),
        ],
        name="venta_conversation",
        allow_reentry=True,
    )
    return [conv]
