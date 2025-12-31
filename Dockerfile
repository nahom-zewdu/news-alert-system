# syntax=docker/dockerfile:1

# Builder stage
FROM python:3.12-slim AS builder

# Install uv (latest official image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

COPY pyproject.toml uv.lock ./

# Install dependencies (without the project itself yet, for better caching)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

COPY . /app

# Install the project itself (editable mode not needed for production)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Runtime stage (small final image)
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/app/.venv"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]