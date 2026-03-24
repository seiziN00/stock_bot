# 🍦 Stock Bot – Inventario de Marcianos

Bot de Telegram para gestionar el inventario de marcianos (helados) usando Google Sheets como base de datos.

## Comandos

| Comando   | Descripción                                                                                            |
| --------- | ------------------------------------------------------------------------------------------------------ |
| `/start`  | Mensaje de bienvenida                                                                                  |
| `/help`   | Lista de comandos disponibles                                                                          |
| `/add`    | Añadir stock (entrada) – selecciona producto con botones, luego ingresa cantidad                       |
| `/venta`  | Registrar venta (salida) – selecciona múltiples productos con botones toggle, luego ingresa cantidades |
| `/stock`  | Ver stock actual de todos los productos                                                                |
| `/poco`   | Ver productos con stock ≤ 10                                                                           |
| `/cancel` | Cancelar operación en curso                                                                            |

## Estructura

```
stock_bot/
├── main.py          # Entry point – registra handlers e inicia polling
├── config.py        # Variables de entorno y configuración
├── sheets.py        # Capa de servicio para Google Sheets
├── handlers/
│   ├── __init__.py
│   ├── start.py     # /start, /help
│   ├── stock.py     # /stock, /poco
│   ├── add.py       # /add (ConversationHandler)
│   └── venta.py     # /venta (ConversationHandler con toggle buttons)
├── credenciales.json  (gitignored)
├── .env               (gitignored)
└── pyproject.toml
```

## Setup

1. Crear archivo `.env`:

   ```
   TELEGRAM_TOKEN=tu_token
   SPREADSHEET_ID=id_de_tu_spreadsheet
   ```

2. Colocar `credenciales.json` (service account de Google) en la raíz.

3. Instalar dependencias:

   ```bash
   uv sync
   ```

4. Ejecutar:
   ```bash
   uv run python main.py
   ```
