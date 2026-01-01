# Use the official Python image with Python as the base
FROM python:3.11-slim

# Set the working directory inside the container to /app
WORKDIR /app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tu código
COPY . .

# (Opcional) si tu app corre por 8000
EXPOSE 8000

# Ajusta si tu "app" no se llama así
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
