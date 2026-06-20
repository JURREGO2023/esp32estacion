FROM python:3.10-slim

WORKDIR /app

# Copiamos e instalamos las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Comando para iniciar el servidor MCP
CMD ["python", "mcp_app.py"]