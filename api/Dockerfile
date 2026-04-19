FROM python:3.12-slim

# Crear usuario no root
RUN useradd -m appuser

WORKDIR /app

# Copiar requirements primero (mejor cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Usar usuario no root
USER appuser

# Puerto correcto (8000)
EXPOSE 8000

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# Ejecutar app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
