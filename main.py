import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import pywhatkit as kit
from dotenv import load_dotenv
import os

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Definir alcance (permisos)
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    #"https://www.googleapis.com/auth/drive"
]

# Cargar credenciales
creds = Credentials.from_service_account_file(
    "credenciales.json",
    scopes=scopes
)

# Autorizar cliente
client = gspread.authorize(creds)

# Abrir archivo por id
spreadsheet = client.open_by_key(SPREADSHEET_ID)

# Seleccionar hoja
sheet = spreadsheet.sheet1

# ===== WHATSAPP =====
def verificar_stock(df):
    df["Stock"] = df["Entrada"] - df["Salida"]
    low_stock = df[df["Stock"] < 40]

    if not low_stock.empty:
        mensaje = "⚠️ STOCK BAJO:\n\n"

        for _, row in low_stock.iterrows():
            mensaje += f"{row['Producto']}: {row['Stock']} unidades\n"
        
        enviar_alerta(mensaje)

def enviar_alerta(mensaje):
    kit.sendwhatmsg_instantly(
        PHONE_NUMBER, 
        mensaje,
        wait_time=10,
        tab_close=True
    )

#verificar_stock(df)


# ===== TELEGRAM =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Hola!, soy un bot de stock."
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=update.message.text
    )

async def stock(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Consultando stock..."
    )

    # Leer datos
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    df["Stock"] = df["Entrada"] - df["Salida"]

    mensaje = "📦 *STOCK ACTUAL*\n"
    mensaje += "```text\n"

    for s, q, in zip(df["Producto"], df["Stock"]):
        mensaje += f"{s} → {q}\n"

    mensaje += "```"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=mensaje,
        parse_mode=ParseMode.MARKDOWN_V2
    )

async def poco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Consultando pocos..."
    )

    # Leer datos
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    df["Stock"] = df["Entrada"] - df["Salida"]
    low_stock = df[df["Stock"] < 10]

    if not low_stock.empty:
        mensaje = "⚠️ *STOCK BAJO*\n"
        mensaje += "```text\n"

        for _, row in low_stock.iterrows():
            mensaje += f"{row['Producto']} → {row['Stock']}\n"

        mensaje += "```"

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=mensaje,
            parse_mode=ParseMode.MARKDOWN_V2
        )

# ===== HANDLER DE ERROR =====
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="No entiendo ese comando"
    )

if __name__ == "__main__":
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Handlers
    start_handler = CommandHandler("start", start)
    stock_handler = CommandHandler("stock", stock)
    poco_handler = CommandHandler("poco", poco)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    # Agregar handlers
    application.add_handler(start_handler)
    application.add_handler(stock_handler)
    application.add_handler(poco_handler)
    application.add_handler(echo_handler)
    application.add_handler(unknown_handler)

    print("Iniciando bot...")
    application.run_polling()