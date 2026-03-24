"""Google Sheets service layer – all spreadsheet I/O lives here."""

from __future__ import annotations

from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

import config


def _get_client() -> gspread.Client:
    creds = Credentials.from_service_account_file(
        config.CREDENTIALS_FILE,
        scopes=config.SCOPES,
    )
    return gspread.authorize(creds)


_client = _get_client()
_spreadsheet = _client.open_by_key(config.SPREADSHEET_ID)


def _registros() -> gspread.Worksheet:
    return _spreadsheet.worksheet(config.SHEET_REGISTROS)


def _productos() -> gspread.Worksheet:
    return _spreadsheet.worksheet(config.SHEET_PRODUCTOS)


# ── Read helpers ─────────────────────────────────────────────────────────────


def get_productos() -> list[str]:
    """Return the list of product names from the Productos sheet."""
    return _productos().col_values(1)


def get_stock() -> dict[str, int]:
    """Return {product: stock} for every product that has records.

    Stock = sum(Entrada) − sum(Salida) per product.
    """
    records = _registros().get_all_records()
    stock: dict[str, int] = {}
    for row in records:
        name = str(row["Producto"])
        stock[name] = stock.get(name, 0) + int(row["Entrada"]) - int(row["Salida"])
    return stock


def get_low_stock(threshold: int = config.LOW_STOCK_THRESHOLD) -> dict[str, int]:
    """Return only products whose stock is ≤ *threshold*."""
    return {p: q for p, q in get_stock().items() if q <= threshold}


# ── Write helpers ────────────────────────────────────────────────────────────


def _now_parts() -> tuple[str, str]:
    now = datetime.now()
    return now.strftime(config.DATE_FORMAT), now.strftime(config.TIME_FORMAT)


def add_entrada(producto: str, cantidad: int) -> None:
    """Append an *entrada* row (stock in)."""
    fecha, hora = _now_parts()
    _registros().append_row([producto, cantidad, 0, fecha, hora])


def add_salida(producto: str, cantidad: int) -> None:
    """Append a *salida* row (stock out / sale)."""
    fecha, hora = _now_parts()
    _registros().append_row([producto, 0, cantidad, fecha, hora])


def add_salidas(items: list[tuple[str, int]]) -> None:
    """Batch-append multiple *salida* rows in a single API call."""
    fecha, hora = _now_parts()
    rows = [[producto, 0, cantidad, fecha, hora] for producto, cantidad in items]
    _registros().append_rows(rows)
