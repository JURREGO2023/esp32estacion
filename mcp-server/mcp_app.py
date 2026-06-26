import os
import mysql.connector
from fastmcp import FastMCP

# Inicializamos el servidor FastMCP
mcp = FastMCP("EstacionMeteorologicaIoT")

# Configuración de BD basada en tu esp-database.php
DB_HOST = os.environ.get("DB_HOST", "db")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Utipec2025*")
DB_NAME = os.environ.get("DB_NAME", "estacionesp32")

def get_db_connection():
    """Crea y retorna la conexión a la base de datos."""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

# LA SUPER HERRAMIENTA ÚNICA
@mcp.tool()
def obtener_reporte_climatico_completo() -> str:
    """Extrae TODOS los datos climáticos al mismo tiempo: actual, mínimos y promedios para la IA."""
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        
        # 1. Última lectura (Actual)
        cursor.execute("SELECT value1, value2, value3, reading_time FROM SensorData ORDER BY reading_time DESC LIMIT 1")
        ultima = cursor.fetchone()
        
        # 2. Temperatura mínima histórica
        cursor.execute("SELECT value1, value2, reading_time FROM SensorData ORDER BY value1 ASC LIMIT 1")
        minima = cursor.fetchone()
        
        # 3. Promedios (últimos 1000 registros)
        cursor.execute("SELECT AVG(value1) as t_avg, AVG(value2) as h_avg FROM (SELECT value1, value2 FROM SensorData ORDER BY reading_time DESC LIMIT 1000) AS sub")
        promedios = cursor.fetchone()
        
        if not ultima:
            return "Aún no hay datos registrados en la estación."

        # Armamos el paquete de texto consolidado para enviarlo a Vercel
        reporte = (
            f"--- REPORTE CLIMÁTICO CONSOLIDADO ESP32 ---\n"
            f"1. LECTURA ACTUAL: Temperatura {ultima['value1']}°C, Humedad {ultima['value2']}%, Presión {ultima['value3']}hPa (Fecha: {ultima['reading_time']})\n"
            f"2. RÉCORD MÍNIMO HISTÓRICO: {minima['value1']}°C con {minima['value2']}% de humedad (Fecha: {minima['reading_time']})\n"
            f"3. TENDENCIA RECIENTE (Últimos 1000 registros): Temperatura promedio {round(promedios['t_avg'], 2)}°C, Humedad promedio {round(promedios['h_avg'], 2)}%\n"
        )
        
        return reporte

    except Exception as err:
        return f"Error al consultar la base de datos: {err}"
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    # Arrancamos el servidor FastMCP
    mcp.run(transport="sse", host="0.0.0.0", port=8000)