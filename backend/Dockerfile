FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY backend/ .

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    /root/.local/bin/uv sync --frozen --no-dev

ENV PATH="/root/.local/bin:$PATH"

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]