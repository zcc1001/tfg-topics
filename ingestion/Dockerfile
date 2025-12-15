FROM python:3.11-slim

WORKDIR /app

# Establecer la variable de entorno PYTHONPATH para que los imports funcionen
# Se asume que la aplicación se ejecuta desde un directorio que contiene 'ingestion'
ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY requirements.txt /app/ingestion/requirements.txt
RUN pip install --no-cache-dir -r /app/ingestion/requirements.txt

COPY src /app/ingestion/src

CMD ["python", "ingestion/src/main.py"]