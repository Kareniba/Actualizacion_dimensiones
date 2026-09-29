import os
import pandas as pd
from dotenv import load_dotenv
from utils.reglas import eliminar_espacios, renombrar_columnas, conversion_mayusculas
from db_utils.load import actualizar_dimension

load_dotenv()

ruta_archivos = os.getenv("RUTA_ARCHIVOS_DIM", "csvs_dim")

# 1. Extraer
tiendas = pd.read_csv(os.path.join(ruta_archivos, "tiendas_erp.csv"), dtype=str)

# 2. Transformar
mapeo_columnas = {
    "COD_TIENDA": "TiendaID",
    "NOMBRE_TIENDA": "NombreTienda",
    "CIUDAD": "Ciudad",
    "REGION": "Region",
    "FECHA_APERTURA": "FechaApertura",
}

tiendas = renombrar_columnas(tiendas, mapeo_columnas)

columnas = ["TiendaID", "NombreTienda", "Ciudad", "Region", "FechaApertura"]
tiendas = tiendas[columnas]

tiendas = eliminar_espacios(tiendas, columnas)
tiendas = conversion_mayusculas(tiendas, ["TiendaID"])

# La fecha viene del ERP como dd/mm/aaaa; en la dimensión se guarda como aaaa-mm-dd
tiendas["FechaApertura"] = pd.to_datetime(tiendas["FechaApertura"], format="%d/%m/%Y").dt.strftime("%Y-%m-%d")

# Una tienda por ID (si viene repetida, nos quedamos con el último registro)
tiendas = tiendas.drop_duplicates(subset=["TiendaID"], keep="last")

# 3. Cargar (insertar nuevas + actualizar existentes)
insertados, actualizados = actualizar_dimension(tiendas, "DimTienda", "TiendaID")

print(f"DimTienda -> {insertados} insertados, {actualizados} actualizados.")