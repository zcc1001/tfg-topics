FROM python:3.11-slim

WORKDIR /app

# Establecer la variable de entorno PYTHONPATH para que los imports funcionen
ENV PYTHONPATH=/app

# Copiar el fichero de requisitos e instalar las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente de la aplicación
COPY ../ingestion/src ./src

# Comando para ejecutar la aplicación
ENTRYPOINT ["python", "src/main.py"]