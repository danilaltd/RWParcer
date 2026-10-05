"""Integration tests using Testcontainers PostgreSQL and Alembic migrations."""

from __future__ import annotations

import asyncio
import datetime
import uuid
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest
from app.application.facade import Facade
from app.domain.entities import User
from app.domain.value_objects import Station, Train
from app.infrastructure.db.models import Base
from app.infrastructure.db.repositories import (
    FavoritePostgresRepository,
    RolePostgresRepository,
    ServiceRoutePostgresRepository,
    UserPostgresRepository,
    UserRolePostgresRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.community.postgres import PostgresContainer

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from app.domain.protocols import Logger


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def async_db_url(postgres_container: PostgresContainer) -> str:
    url: str = postgres_container.get_connection_url(driver="asyncpg")
    return url


@pytest.fixture(autouse=True)
def run_migrations(async_db_url: str) -> None:
    async def _up() -> None:
        engine = create_async_engine(async_db_url)
        async with engine.begin() as conn:
            for schema in ("identity", "transport", "monitoring", "messaging", "bot", "audit"):
                await conn.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {schema};")
            await conn.run_sync(Base.metadata.create_all)
        await engine.dispose()

    asyncio.run(_up())


@pytest.fixture
async def db_session_factory(
    async_db_url: str,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    engine = create_async_engine(async_db_url, echo=False, future=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    yield factory
    await engine.dispose()


@pytest.fixture
def logger() -> Logger:
    class DummyLogger:
        def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
            pass

        def info(self, message: str, *args: Any, **kwargs: Any) -> None:
            pass

        def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
            pass

        def error(self, message: str, *args: Any, **kwargs: Any) -> None:
            pass

    return DummyLogger()


@pytest.mark.asyncio
async def test_integration_user_and_favorites(
    db_session_factory: async_sessionmaker[AsyncSession], logger: Logger
) -> None:
    role = RolePostgresRepository(db_session_factory)
    user_role = UserRolePostgresRepository(db_session_factory, role)
    users_repo = UserPostgresRepository(db_session_factory, user_role)
    transport_repo = ServiceRoutePostgresRepository(db_session_factory)
    fav_repo = FavoritePostgresRepository(db_session_factory, transport_repo)

    uid = uuid.uuid4()
    await users_repo.add_user(User(id=uid, telegram_user_id=123, telegram_chat_id=123))

    train = Train(
        train_type="p",
        train_number="701",
        main_station_from=Station("Минск", "MSK"),
        main_station_to=Station("Брест", "BRS"),
        station_from=Station("Минск", "MSK"),
        station_to=Station("Брест", "BRS"),
        from_time=datetime.time(7, 0),
        to_time=datetime.time(10, 0),
        train_days="",
        train_days_except="",
        duration_minutes=180,
    )

    facade = Facade(
        users=users_repo,
        transport=transport_repo,
        subscriptions=MagicMock(),
        favorites=fav_repo,
        notifications=MagicMock(),
        messages=MagicMock(),
        rw=MagicMock(),
    )

    await facade.add_to_favorites(uid, train)
    favorites = await facade.get_favorites(uid)
    assert len(favorites) == 1
    assert favorites[0].train_number == "701"
