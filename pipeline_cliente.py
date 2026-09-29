import os
import pandas as pd
from dotenv import load_dotenv
from utils.reglas import eliminar_duplicados, eliminar_espacios, renombrar_columnas, conversion_mayusculas
from db_utils.load import actualizar_dimension

load_dotenv()

ruta_archivos = os.getenv("RUTA_ARCHIVOS_DIM", "csvs_dim")

# 1. Extraer
clientes = pd.read_csv(os.path.join(ruta_archivos, "clientes_erp.csv"), dtype=str)

# 2. Transformar
mapeo_columnas = {
    "COD_CLIENTE": "ClienteID",
    "NOMBRE_CLIENTE": "NombreCliente",
    "GENERO": "Genero",
    "RANGO_EDAD": "RangoEdad",
    "CIUDAD": "Ciudad",
    "SEGMENTO": "SegmentoCliente",
}

clientes = renombrar_columnas(clientes, mapeo_columnas)

columnas = ["ClienteID", "NombreCliente", "Genero", "RangoEdad", "Ciudad", "SegmentoCliente"]
clientes = clientes[columnas]

clientes = eliminar_espacios(clientes, columnas)
clientes = conversion_mayusculas(clientes, ["ClienteID", "Genero"])

# Segmento con formato Nuevo / Regular / VIP
clientes["SegmentoCliente"] = clientes["SegmentoCliente"].str.capitalize().replace({"Vip": "VIP"})

# Un cliente por ID (si viene repetido, nos quedamos con el último registro)
clientes = clientes.drop_duplicates(subset=["ClienteID"], keep="last")

# 3. Cargar (insertar nuevos + actualizar existentes)
insertados, actualizados = actualizar_dimension(clientes, "DimCliente", "ClienteID")

print(f"DimCliente -> {insertados} insertados, {actualizados} actualizados.")