FROM python:3.14.4-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv \
    && uv sync --frozen --no-dev --extra neo4j --no-install-project

COPY main.py ./
COPY app ./app
COPY config ./config
COPY contracts ./contracts
COPY data ./data
COPY graph ./graph

RUN uv sync --frozen --no-dev --extra neo4j \
    && mkdir -p /data

ENV PYTHONUNBUFFERED=1
ENV LUMEN_DATA_DIR=/data
ENV DUCKDB_PATH=/data/lumen.duckdb
ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
