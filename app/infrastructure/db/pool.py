from __future__ import annotations

from typing import TYPE_CHECKING, Any

import asyncpg

if TYPE_CHECKING:
    from app.config import DatabaseSettings


class ConnectionPool:
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    @staticmethod
    async def create(settings: DatabaseSettings) -> ConnectionPool:
        pool = await asyncpg.create_pool(
            dsn=settings.connection_string,
            min_size=5,
            max_size=20,
        )
        if pool is None:
            raise RuntimeError("Failed to create asyncpg pool")
        return ConnectionPool(pool)

    @staticmethod
    async def create_from_url(dsn: str) -> ConnectionPool:
        pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=5,
            max_size=20,
        )
        if pool is None:
            raise RuntimeError("Failed to create asyncpg pool")
        return ConnectionPool(pool)

    async def close(self) -> None:
        await self._pool.close()

    def acquire(self) -> asyncpg.pool.PoolConnectionHolder:
        return self._pool.acquire()

    async def execute(self, query: str, *args: Any) -> str:
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args: Any) -> list[asyncpg.Record]:
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchval(self, query: str, *args: Any) -> object:
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def fetchrow(self, query: str, *args: Any) -> asyncpg.Record | None:
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)


class PoolHolder:
    _pool: ConnectionPool | None = None

    @classmethod
    async def initialize(cls, settings: DatabaseSettings) -> None:
        cls._pool = await ConnectionPool.create(settings)

    @classmethod
    def get_pool(cls) -> ConnectionPool:
        if cls._pool is None:
            raise RuntimeError("Pool not initialized")
        return cls._pool

    @classmethod
    async def close(cls) -> None:
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
