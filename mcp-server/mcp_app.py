import os
import mysql.connector
from fastmcp import FastMCP

# ==========================
# MCP
# ==========================
mcp = FastMCP("EstacionMeteorologicaIoT")

# ==========================
# Configuración BD
# ==========================
DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Utipec2025*")
DB_NAME = os.getenv("DB_NAME", "estacionesp32")


def get_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def query_one(sql, params=None):
    conexion = get_db()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(sql, params or ())
        return cursor.fetchone()

    finally:
        cursor.close()
        conexion.close()


# ============================================================
# 1. LECTURA ACTUAL
# ============================================================

@mcp.tool()
def obtener_lectura_actual():
    """
    Devuelve la última lectura registrada por la estación meteorológica.

    Úsese cuando el usuario pregunte:

    - clima actual
    - temperatura actual
    - humedad actual
    - presión actual
    - cómo está el clima
    """

    sql = """
        SELECT
            value1,
            value2,
            value3,
            reading_time
        FROM SensorData
        ORDER BY reading_time DESC
        LIMIT 1
    """

    dato = query_one(sql)

    if not dato:
        return "No existen registros."

    return (
        f"Temperatura: {dato['value1']} °C\n"
        f"Humedad: {dato['value2']} %\n"
        f"Presión: {dato['value3']} hPa\n"
        f"Fecha: {dato['reading_time']}"
    )


# ============================================================
# 2. TEMPERATURA MÍNIMA POR FECHA
# ============================================================

@mcp.tool()
def obtener_temperatura_minima_por_fecha(fecha: str):
    """
    Obtiene la temperatura mínima registrada en una fecha.

    Formato:

    YYYY-MM-DD

    Ejemplo:

    2026-06-28
    """

    sql = """
        SELECT
            MIN(value1) temperatura
        FROM SensorData
        WHERE DATE(reading_time)=%s
    """

    dato = query_one(sql, (fecha,))

    if dato["temperatura"] is None:
        return f"No existen registros para {fecha}"

    return f"La temperatura mínima del {fecha} fue {dato['temperatura']} °C"


# ============================================================
# 3. TEMPERATURA MÁXIMA POR FECHA
# ============================================================

@mcp.tool()
def obtener_temperatura_maxima_por_fecha(fecha: str):
    """
    Obtiene la temperatura máxima registrada en una fecha.

    Formato:

    YYYY-MM-DD
    """

    sql = """
        SELECT
            MAX(value1) temperatura
        FROM SensorData
        WHERE DATE(reading_time)=%s
    """

    dato = query_one(sql, (fecha,))

    if dato["temperatura"] is None:
        return f"No existen registros para {fecha}"

    return f"La temperatura máxima del {fecha} fue {dato['temperatura']} °C"


# ============================================================
# 4. PROMEDIO DIARIO
# ============================================================

@mcp.tool()
def obtener_promedio_por_fecha(fecha: str):
    """
    Calcula el promedio de temperatura, humedad y presión para una fecha.

    Formato:

    YYYY-MM-DD
    """

    sql = """
        SELECT

        ROUND(AVG(value1),2) temperatura,

        ROUND(AVG(value2),2) humedad,

        ROUND(AVG(value3),2) presion

        FROM SensorData

        WHERE DATE(reading_time)=%s
    """

    dato = query_one(sql, (fecha,))

    if dato["temperatura"] is None:
        return f"No existen registros para {fecha}"

    return (
        f"Promedios del {fecha}\n\n"
        f"Temperatura: {dato['temperatura']} °C\n"
        f"Humedad: {dato['humedad']} %\n"
        f"Presión: {dato['presion']} hPa"
    )


# ============================================================
# 5. REPORTE COMPLETO
# ============================================================

@mcp.tool()
def obtener_reporte_climatico_completo():
    """
    Genera un resumen completo del estado de la estación meteorológica.

    Incluye:

    • lectura actual

    • temperatura mínima histórica

    • temperatura máxima histórica

    • promedio reciente

    Es la herramienta ideal cuando el usuario pide un reporte general.
    """

    conexion = get_db()
    cursor = conexion.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                value1,
                value2,
                value3,
                reading_time
            FROM SensorData
            ORDER BY reading_time DESC
            LIMIT 1
        """)

        actual = cursor.fetchone()

        cursor.execute("""
            SELECT
                MIN(value1) minima,
                MAX(value1) maxima,
                ROUND(AVG(value1),2) promedio
            FROM SensorData
        """)

        estadisticas = cursor.fetchone()

        if not actual:
            return "No existen registros."

        return f"""
REPORTE CLIMÁTICO

Lectura actual

Temperatura : {actual['value1']} °C
Humedad     : {actual['value2']} %
Presión     : {actual['value3']} hPa
Fecha        : {actual['reading_time']}

Estadísticas

Temperatura mínima : {estadisticas['minima']} °C
Temperatura máxima : {estadisticas['maxima']} °C
Temperatura promedio : {estadisticas['promedio']} °C
"""

    finally:
        cursor.close()
        conexion.close()


# ============================================================
# INICIO MCP
# ============================================================

if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="0.0.0.0",
        port=8000
    )