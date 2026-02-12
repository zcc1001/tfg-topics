FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app/src

COPY requirement.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirement.txt

COPY src ./src
COPY .streamlit ./.streamlit

EXPOSE 8501

CMD ["streamlit", "run", "src/webapp/main.py", "--server.address=0.0.0.0", "--server.port=8501"]
