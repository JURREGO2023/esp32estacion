import streamlit as st
import mysql.connector
import os
import google.generativeai as genai

# Configuración visual de la página web
st.set_page_config(page_title="Estación IoT - Chat", page_icon="⛅")
st.title("⛅ Asistente Virtual: Estación Meteorológica ESP32")
st.markdown("¡Hola! Pregúntame sobre el clima actual o el histórico de nuestra estación.")

# Función para consultar la base de datos local
def consultar_clima():
    try:
        conexion = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'db'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', 'Utipec2025*'),
            database=os.environ.get('DB_NAME', 'estacionesp32')
        )
        cursor = conexion.cursor(dictionary=True)
        # Ajusta "SensorData" al nombre real de tu tabla si es diferente
        cursor.execute("SELECT temperatura, humedad, fecha FROM SensorData ORDER BY fecha DESC LIMIT 1")
        resultado = cursor.fetchone()
        
        if resultado:
            return f"Última lectura: {resultado['temperatura']}°C, Humedad: {resultado['humedad']}%. Registrado el: {resultado['fecha']}."
        return "Aún no hay datos en la estación."
    except Exception as e:
        return f"Error leyendo la base de datos: {e}"
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

# Configurar el chat interactivo
if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# Mostrar historial de mensajes
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

# Caja de texto para que el usuario escriba
if prompt := st.chat_input("Ej: ¿Cuál fue la última temperatura registrada?"):
    # Guardar y mostrar pregunta del usuario
    st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del bot
    with st.chat_message("assistant"):
        datos_reales = consultar_clima()
        
        # Aquí puedes conectar Gemini para que analice los datos, 
        # por ahora responde directamente con el dato de la base de datos.
        respuesta = f"Revisando los sensores de la ESP32... 📊\n\n{datos_reales}"
        st.markdown(respuesta)
        st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})