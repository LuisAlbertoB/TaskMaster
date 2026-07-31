# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalar dependencias del sistema para psycopg2 y Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar el código fuente del proyecto
COPY . .

# Crear directorio de media (se monta como volumen)
RUN mkdir -p /app/media/tareas/originales /app/media/tareas/thumbnails

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Puerto de exposición
EXPOSE 8000

# Comando de inicio: Gunicorn en producción
CMD ["gunicorn", "src.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
