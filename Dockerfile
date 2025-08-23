FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 🔽 Paquetes necesarios para compilar psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev python3-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir gunicorn

COPY . .

ENV DJANGO_SETTINGS_MODULE=main.settings
CMD ["sh","-c","python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn main.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --threads ${WEB_THREADS:-1} --timeout ${WEB_TIMEOUT:-120}"]
