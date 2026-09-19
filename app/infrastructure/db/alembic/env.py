"""Alembic migration environment.

Runs against the same ``core_db`` database as the application. The URL is
taken from ``DATABASE_URL_SYNC`` when provided, otherwise from
``DATABASE_URL`` (the app runtime URL). Because only ``asyncpg`` is a hard
dependency, online migrations execute through the async engine even for a
sync-style URL by normalising ``postgres://``/``postgresql://`` prefixes.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import load_settings
from app.infrastructure.db import models

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection

config = context.config

if not config.get_main_option("sqlalchemy.url"):
    settings = load_settings()
    url = settings.database.sync_connection_string or settings.database.connection_string
    config.set_main_option("sqlalchemy.url", url)

target_metadata = models.Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (emit SQL to ``script.output``)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations online via the asyncpg driver."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
