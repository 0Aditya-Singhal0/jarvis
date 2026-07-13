ARG PYTHON_IMAGE
FROM ${PYTHON_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN addgroup --system jarvis && adduser --system --ingroup jarvis jarvis

COPY requirements.lock ./
RUN python -m pip install --no-cache-dir --only-binary=:all: --require-hashes -r requirements.lock

COPY src ./src
COPY alembic.ini ./
COPY migrations ./migrations

USER jarvis
EXPOSE 8080
CMD ["python", "-m", "uvicorn", "jarvis_api.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
