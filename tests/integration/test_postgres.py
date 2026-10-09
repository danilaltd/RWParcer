"""Integration tests using Testcontainers PostgreSQL."""

from __future__ import annotations

import asyncio
import datetime
import pathlib
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import asyncpg
import pytest
from app.application.facade import Facade
from app.domain.value_objects import Station, SubscriptionDetails, Train
from app.infrastructure.db.pool import ConnectionPool
from app.infrastructure.db.repositories import (
    AvailabilitySnapshotPostgresRepository,
    FavoritePostgresRepository,
    MessagePostgresRepository,
    NotificationPostgresRepository,
    RolePostgresRepository,
    ServiceRoutePostgresRepository,
    SubscriptionPostgresRepository,
    UserPostgresRepository,
    UserRolePostgresRepository,
)
from testcontainers.community.postgres import PostgresContainer

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer]:
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def async_db_url(postgres_container: PostgresContainer) -> str:
    return postgres_container.get_connection_url(driver=None)


@pytest.fixture(autouse=True)
def run_migrations(async_db_url: str) -> None:
    async def _up() -> None:
        pool = await asyncpg.create_pool(async_db_url)
        if pool is None:
            raise RuntimeError("Failed to create pool")
        async with pool.acquire() as conn:
            for schema in ("identity", "transport", "monitoring", "messaging", "bot", "audit"):
                await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema};")

            schema_sql = pathlib.Path("db-test/001_schema.sql").read_text(encoding="utf-8")
            await conn.execute(schema_sql)
        await pool.close()

    asyncio.run(_up())


@pytest.fixture
async def db_pool(async_db_url: str) -> AsyncGenerator[ConnectionPool]:
    pool = await ConnectionPool.create_from_url(async_db_url)
    yield pool
    await pool.close()


@pytest.mark.asyncio
async def test_integration_user_and_favorites(db_pool: ConnectionPool) -> None:
    role_repo = RolePostgresRepository(db_pool)
    user_role_repo = UserRolePostgresRepository(db_pool, role_repo)
    users_repo = UserPostgresRepository(db_pool, user_role_repo)
    transport_repo = ServiceRoutePostgresRepository(db_pool)
    fav_repo = FavoritePostgresRepository(db_pool, transport_repo)
    snapshot_repo = AvailabilitySnapshotPostgresRepository(db_pool)
    subscription_repo = SubscriptionPostgresRepository(db_pool, transport_repo, snapshot_repo)
    notifications_repo = NotificationPostgresRepository(db_pool)
    messages_repo = MessagePostgresRepository(db_pool)

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
        subscriptions=subscription_repo,
        favorites=fav_repo,
        notifications=notifications_repo,
        messages=messages_repo,
        rw=MagicMock(),
    )

    moderator_uid = await facade.register_user(
        telegram_user_id=123, telegram_chat_id=123, username=None, display_name="abc"
    )

    user_uid = await facade.register_user(
        telegram_user_id=456, telegram_chat_id=456, username=None, display_name="def"
    )

    moderator_by_id = await facade.get_user_by_id(moderator_uid, moderator_uid)
    assert moderator_by_id.id == moderator_uid
    assert moderator_by_id.telegram_user_id == 123
    assert moderator_by_id.is_moderator

    user_by_id = await facade.get_user_by_id(user_uid, user_uid)
    assert user_by_id.id == user_uid
    assert user_by_id.telegram_user_id == 456
    assert not user_by_id.is_moderator

    await facade.add_to_favorites(moderator_uid, train)

    await facade.subscribe(moderator_uid, SubscriptionDetails(train, datetime.date.today()))

    favorites = await facade.get_favorites(moderator_uid)
    assert len(favorites) == 1
    assert favorites[0].train_number == "701"

    await facade.send_feedback(moderator_uid, "test_msg")

    notifications = await facade.pop_notifications()
    assert len(notifications) == 1
    assert notifications[0].user_id == moderator_uid
    assert "test_msg" in notifications[0].content

    users = await facade.get_users(moderator_uid, datetime.timedelta(seconds=1))
    assert len(users) == 2
