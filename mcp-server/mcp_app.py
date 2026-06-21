import os
import mysql.connector
from fastmcp import FastMCP

# Inicializamos el servidor FastMCP
mcp = FastMCP("EstacionMeteorologicaIoT")

# Configuración de BD basada en tu esp-database.php
# Usamos os.environ para que funcione perfecto con Docker Compose
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

@mcp.tool()
def obtener_ultima_lectura() -> str:
    """Obtiene la temperatura, humedad y presión más reciente de la estación meteorológica IoT."""
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        
        # Mapeamos value1 (Temp), value2 (Hum) y value3 (Presión)
        query = "SELECT value1, value2, value3, reading_time FROM SensorData ORDER BY reading_time DESC LIMIT 1"
        cursor.execute(query)
        registro = cursor.fetchone()
        
        if registro:
            return (f"Última lectura registrada el {registro['reading_time']}:\n"
                    f"- Temperatura: {registro['value1']}°C\n"
                    f"- Humedad: {registro['value2']}%\n"
                    f"- Presión: {registro['value3']} hPa")
        else:
            return "Aún no hay datos registrados en la estación."

    except mysql.connector.Error as err:
        return f"Error al conectar con la base de datos: {err}"
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

@mcp.tool()
def obtener_estadisticas_clima(limite: int = 50) -> str:
    """
    Obtiene los promedios de temperatura, humedad y presión de los últimos registros.
    limite: Cantidad de registros recientes a evaluar (ej. 50).
    """
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        
        # Calculamos los promedios usando la misma lógica de tu PHP
        query = f"""
            SELECT 
                AVG(value1) as avg_temp, 
                AVG(value2) as avg_hum, 
                AVG(value3) as avg_presion 
            FROM (SELECT value1, value2, value3 FROM SensorData ORDER BY reading_time DESC LIMIT {limite}) AS subquery
        """
        cursor.execute(query)
        stats = cursor.fetchone()
        
        if stats and stats['avg_temp'] is not None:
            return (f"Estadísticas promedio de las últimas {limite} lecturas:\n"
                    f"- Temperatura Promedio: {round(stats['avg_temp'], 2)}°C\n"
                    f"- Humedad Promedio: {round(stats['avg_hum'], 2)}%\n"
                    f"- Presión Promedio: {round(stats['avg_presion'], 2)} hPa")
        else:
            return "No hay suficientes datos para calcular estadísticas."

    except mysql.connector.Error as err:
        return f"Error de base de datos: {err}"
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

def obtener_temperatura_minima() -> str:
    """
    Busca en la base de datos el registro histórico con la temperatura más baja.
    """
    try:
        # Asegúrate de usar las variables de entorno o credenciales que ya tienes en tu código
        conexion = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conexion.cursor(dictionary=True)
        
        # Ajusta "SensorData" al nombre real de tu tabla de la ESP32 (ej. 'datos_clima', 'lecturas')
        # Ajusta "temperatura", "humedad" y "fecha" a los nombres reales de tus columnas
        query = "SELECT temperatura, humedad, fecha FROM SensorData ORDER BY temperatura ASC LIMIT 1"
        cursor.execute(query)
        resultado = cursor.fetchone()
        
        if resultado:
            return f"❄️ La temperatura histórica más baja fue {resultado['temperatura']}°C (con {resultado['humedad']}% de humedad), registrada el {resultado['fecha']}."
        else:
            return "No hay registros en la base de datos todavía."
            
    except Exception as e:
        return f"Error al consultar la temperatura mínima: {str(e)}"
    finally:
        # Cerramos la conexión para no saturar Dokploy
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    # Arrancamos el servidor FastMCP
    mcp.run(transport="sse", host="0.0.0.0", port=8000)