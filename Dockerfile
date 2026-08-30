FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml main.py ./
COPY app ./app
COPY contracts ./contracts
COPY graph ./graph

RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1
ENV LUMEN_DATA_DIR=/data
ENV DUCKDB_PATH=/data/lumen.duckdb
EXPOSE 8000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
