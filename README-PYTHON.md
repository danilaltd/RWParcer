# RWParcer — Python migration

rw.by train seat subscription bot. Python twin of the original C# (.NET 9)
implementation; see `MIGRATION.md` for the full parity notes.

## Architecture (one paragraph)

The bot runs as a single Python process: `app/__main__.py` is the composition
root and starts `BotService` (`app/bot/service.py`), which talks to Telegram
via **manual long-polling** (`Bot.get_updates(offset, timeout=30)`) — there is
no aiogram `Dispatcher` and no FSM `MemoryStorage`/`BaseStorage`. All state is
kept per-chat in `BotSession` (`app/bot/session.py`) and persisted by
`SessionStorage` (`app/bot/storage.py`) into a single consolidated Postgres
database `core_db`, which also holds `users`, `subscriptions`, `favorites`,
`notifications` and `messages`. Every update routes through the
`CommandRouter` (all 41 `CommandNames`) and rewrites the full `sessions`
snapshot, exactly like the C# `PostgresSessionStore`; a background loop polls
`PopNotifications` and delivers seat-change messages to the users.

## Quick start (Docker)

1. Copy the env template and set the required values:

   ```sh
   cp .env.example .env
   # .env: BOT_TOKEN=123456:ABC...   (required)
   #       POSTGRES_PASSWORD=...     (optional, defaults to test_password)
   #       APPSETTINGS_JSON={...}    (optional — overrides individual vars)
   ```

   `BOT_TOKEN` is required. `DATABASE_URL` in `.env` should point at the
   compose service name `postgres_db` (the template already does this).

2. Build and start everything:

   ```sh
   docker compose -f docker-compose.yml up -d --remove-orphans --build
   ```

3. Watch the logs:

   ```sh
   docker compose -f docker-compose.yml logs -f
   docker compose -f docker-compose.yml logs parcer
   ```

4. Stop/cleanup:

   ```sh
   docker compose -f docker-compose.yml down
   docker compose -f docker-compose.yml down -v   # also drop data volumes
   ```

The `parcer` container runs `alembic -c alembic.ini upgrade head` before
starting the bot, so migrations are applied automatically on boot. To apply
migrations manually against a live stack:

```sh
docker compose -f docker-compose.yml exec parcer alembic -c alembic.ini upgrade head
```

## Local development

```sh
python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
pip install -e ".[dev]"
```

Run the bot:

```sh
python -m app
```

Validation:

```sh
.venv/bin/pytest -q
.venv/bin/ruff check app tests
.venv/bin/python -m compileall app tests
```

For local runs set the same env vars as in `.env.example` (`BOT_TOKEN`,
`DATABASE_URL`, `PROXY_MANAGER_URL`, ...). `DATABASE_URL_SYNC` is only needed
when running alembic outside the container.

## Layout

- `app/__main__.py` — composition root (`python -m app`).
- `app/bot/` — long-poll service, command router, handlers, sessions, storage.
- `app/application/` — facade + use cases + background notifier.
- `app/domain/` — entities, value objects, repository protocols, JSON codecs.
- `app/infrastructure/` — SQLAlchemy models/repositories, alembic, rw.by HTTP client, logging.