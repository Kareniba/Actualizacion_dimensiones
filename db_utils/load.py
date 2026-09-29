import sqlite3
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

RUTA_DB = os.getenv("RUTA_DB", "instance")

conn = sqlite3.connect(f"{RUTA_DB}/datacaos_estrella.db")


def actualizar_dimension(df, tabla, pk):
    """
    Actualiza una dimensión: inserta los registros nuevos y actualiza
    los que ya existen (según la llave primaria).

    Returns:
        tuple: (cantidad_insertados, cantidad_actualizados)
    """
    existentes = {fila[0] for fila in conn.execute(f"SELECT {pk} FROM {tabla}")}
    actualizados = int(df[pk].isin(existentes).sum())
    insertados = len(df) - actualizados

    columnas = list(df.columns)
    lista_cols = ", ".join(columnas)
    marcadores = ", ".join("?" for _ in columnas)
    sets = ", ".join(f"{c} = excluded.{c}" for c in columnas if c != pk)

    sql = (
        f"INSERT INTO {tabla} ({lista_cols}) VALUES ({marcadores}) "
        f"ON CONFLICT({pk}) DO UPDATE SET {sets}"
    )

    filas = df.astype(object).where(df.notna(), None).values.tolist()
    conn.executemany(sql, filas)
    conn.commit()
    return insertados, actualizados
