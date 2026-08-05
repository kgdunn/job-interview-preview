FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir -e ".[dev]"

COPY scripts ./scripts
COPY tests ./tests

EXPOSE 8000

CMD ["uvicorn", "batchwatch.api:app", "--host", "0.0.0.0", "--port", "8000"]
