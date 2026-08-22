FROM python:3.12-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY alembic.ini .
COPY app/ ./app/

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "alembic -c alembic.ini upgrade head && python -m app"]