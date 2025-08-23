# Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.46.0-jammy

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
# No instales playwright ni "playwright install --with-deps" aquí; ya viene listo
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir gunicorn

COPY . .

# Importante: usa el módulo WSGI real de tu proyecto (parece ser main.wsgi)
CMD ["sh","-c","python manage.py collectstatic && gunicorn main.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --threads ${WEB_THREADS:-1} --timeout ${WEB_TIMEOUT:-120}"]
