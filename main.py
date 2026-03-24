import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import pywhatkit as kit
from dotenv import load_dotenv
import os

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

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

# Leer datos
data = sheet.get_all_records()
df = pd.DataFrame(data)

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

#-------------------------------------------------------
df["Stock"] = df["Entrada"] - df["Salida"]


print("STOCK ACTUAL:\n---------------")
for s, q, in zip(df["Producto"], df["Stock"]):
    print(f"{s:<10}: {q}")