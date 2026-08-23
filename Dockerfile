FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DAGSTER_HOME=/app/.dagster_home \
    DATA_DIR=/app/data

RUN mkdir -p /app/.dagster_home /app/data/raw /app/data/processed

COPY pyproject.toml ./
COPY mpls_public_safety ./mpls_public_safety
COPY viz ./viz

RUN pip install --no-cache-dir -e .

EXPOSE 3000

CMD ["dagster", "dev", "-h", "0.0.0.0", "-p", "3000", "-m", "mpls_public_safety.definitions"]
