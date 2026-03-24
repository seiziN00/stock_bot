"""Application configuration and environment setup."""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN: str = os.getenv("TELEGRAM_TOKEN", "")

# Google Sheets
SPREADSHEET_ID: str = os.getenv("SPREADSHEET_ID", "")
CREDENTIALS_FILE: str = "credenciales.json"
SCOPES: list[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# Sheet names
SHEET_REGISTROS: str = "Registros"
SHEET_PRODUCTOS: str = "Productos"

# Business rules
LOW_STOCK_THRESHOLD: int = 10
DATE_FORMAT: str = "%d/%m/%Y"
TIME_FORMAT: str = "%H:%M"
