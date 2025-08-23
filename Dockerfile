# Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Solo necesitas esto si usas psycopg2 (no-binary). Si usas psycopg2-binary, puedes borrar este bloque.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev python3-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
# Nota: la imagen ya trae los browsers; aquí instalamos el paquete Python de Playwright (misma versión que la base)
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir gunicorn playwright==1.46.0

COPY . .

ENV DJANGO_SETTINGS_MODULE=main.settings

# 👇 Forzamos worker sync y defaults seguros (1 worker / 1 thread)
CMD ["sh","-c","python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn main.wsgi:application --worker-class sync --workers ${WEB_CONCURRENCY:-1} --threads ${WEB_THREADS:-1} --bind 0.0.0.0:${PORT:-8000} --timeout ${WEB_TIMEOUT:-120}"]
