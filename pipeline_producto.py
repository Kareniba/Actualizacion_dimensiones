import os
import pandas as pd
from dotenv import load_dotenv
from utils.reglas import eliminar_espacios, renombrar_columnas, conversion_mayusculas
from db_utils.load import actualizar_dimension

load_dotenv()

ruta_archivos = os.getenv("RUTA_ARCHIVOS_DIM", "csvs_dim")

# 1. Extraer
productos = pd.read_csv(os.path.join(ruta_archivos, "productos_erp.csv"), dtype=str)

# 2. Transformar
mapeo_columnas = {
    "COD_PRODUCTO": "ProductoID",
    "NOMBRE_PRODUCTO": "NombreProducto",
    "MARCA": "MarcaProducto",
    "CATEGORIA": "NombreCategoria",
    "PROVEEDOR": "NombreProveedor",
    "PAIS_PROVEEDOR": "PaisProveedor",
    "PRECIO_LISTADO": "PrecioListado",
}

productos = renombrar_columnas(productos, mapeo_columnas)

columnas = ["ProductoID", "NombreProducto", "MarcaProducto", "NombreCategoria",
            "NombreProveedor", "PaisProveedor", "PrecioListado"]
productos = productos[columnas]

productos = eliminar_espacios(productos, columnas)
productos = conversion_mayusculas(productos, ["ProductoID"])

# El precio llega como texto; se convierte a número
productos["PrecioListado"] = pd.to_numeric(productos["PrecioListado"])

# Un producto por ID (si viene repetido, nos quedamos con el último registro)
productos = productos.drop_duplicates(subset=["ProductoID"], keep="last")

# 3. Cargar (insertar nuevos + actualizar existentes)
insertados, actualizados = actualizar_dimension(productos, "DimProducto", "ProductoID")

print(f"DimProducto -> {insertados} insertados, {actualizados} actualizados.")