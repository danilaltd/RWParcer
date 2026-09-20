FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY app/ ./app/
COPY alembic.ini .
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "uv run --frozen --no-sync alembic -c alembic.ini upgrade head && uv run --frozen --no-sync python -m app & uv run --frozen --no-sync python -m app.web"]