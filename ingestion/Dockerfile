FROM python:3.11-slim

WORKDIR /app

# Establecer la variable de entorno PYTHONPATH para que los imports funcionen
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Copiar el fichero de requisitos e instalar las dependencias
COPY requirements.txt /app/ingestion/requirements.txt
RUN pip install --no-cache-dir -r /app/ingestion/requirements.txt

# Copiar el código fuente de la aplicación
COPY src /app/ingestion/src

# Comando para ejecutar la aplicación
CMD ["python", "ingestion/src/main.py"]