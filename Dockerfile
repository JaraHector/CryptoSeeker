FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Crear carpeta de logs con permisos correctos para evitar conflictos con el host
RUN mkdir -p logs && chmod 777 logs

CMD ["python", "main.py"]
