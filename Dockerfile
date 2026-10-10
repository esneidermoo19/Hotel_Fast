FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TZ=America/Bogota

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Crea el directorio de medios con dueño appuser para que el volumen nombrado
# media_data herede ese dueño y las subidas no fallen con PermissionError.
RUN mkdir -p /app/media && chown appuser:appuser /app/media

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

EXPOSE 8000

USER appuser

CMD alembic upgrade head && python -m app.seed && uvicorn app.main:app --host 0.0.0.0 --port 8000