"""Async engine / session factory — the DI replacement for ``IAppDbContextFactory``.

Each repository operation opens its *own* ``AsyncSession`` (mirroring
``RepositoryBase`` which created a fresh ``AppDbContext`` per call).
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import DatabaseSettings


def create_engine(connection_string: str) -> AsyncEngine:
    """Build the async engine from an asyncpg URL."""
    if not connection_string:
        raise ValueError("Database connection string is not configured")
    engine = create_async_engine(
        connection_string,
        pool_pre_ping=True,
    )
    return engine


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class EngineHolder:
    """Lazy singleton-style holder so ``alembic`` and tests can share one engine."""

    def __init__(self, settings: DatabaseSettings) -> None:
        self._engine: AsyncEngine | None = None
        self._factory: async_sessionmaker[AsyncSession] | None = None
        self._settings = settings

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            self._engine = create_engine(self._settings.connection_string)
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._factory is None:
            self._factory = create_session_factory(self.engine)
        return self._factory

    async def dispose(self) -> None:
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._factory = None
