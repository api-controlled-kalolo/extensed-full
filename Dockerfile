# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir playwright gunicorn \
 && playwright install --with-deps chromium

COPY . .

# Railway define $PORT; pasamos tunables vía envs
CMD ["sh","-c","gunicorn main.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-1} --threads ${WEB_THREADS:1} --timeout ${WEB_TIMEOUT:-120}"]
