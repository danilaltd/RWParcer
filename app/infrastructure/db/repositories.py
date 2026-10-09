"""PostgreSQL repositories using asyncpg and raw SQL queries."""

from __future__ import annotations

import contextlib
import datetime
import json
import uuid
from typing import TYPE_CHECKING, Any, Protocol

import aiosql
import aiosql.queries

from app.domain.entities import Favorite, Message, Notification, Subscription, User
from app.domain.value_objects import Car, CarType, Station, SubscriptionDetails, Train

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    import asyncpg

    from app.domain.protocols import (
        AvailabilitySnapshotRepository,
        RoleRepository,
        ServiceRouteRepository,
        UserRoleRepository,
    )
    from app.infrastructure.db.pool import ConnectionPool


# Protocol definitions for query files
class RolesQueries(Protocol):
    async def get_role_id(self, conn: Any, code: str) -> int | None: ...

    def get_roles(self, conn: Any) -> AsyncIterator[asyncpg.Record]: ...

    async def insert_role(self, conn: Any, id: int, code: str, name: str) -> None: ...


class UserRolesQueries(Protocol):
    async def get_user_role(
        self, conn: Any, user_id: uuid.UUID, role_id: int
    ) -> asyncpg.Record | None: ...

    def get_user_ids_with_role(self, conn: Any, role_id: int) -> AsyncIterator[asyncpg.Record]: ...

    async def insert_user_role(self, conn: Any, user_id: uuid.UUID, role_id: int) -> None: ...

    async def delete_user_role(self, conn: Any, user_id: uuid.UUID, role_id: int) -> None: ...


class UsersQueries(Protocol):
    async def get_user_by_id(self, conn: Any, id: uuid.UUID) -> asyncpg.Record | None: ...

    async def get_user_by_telegram_id(
        self, conn: Any, telegram_user_id: int
    ) -> asyncpg.Record | None: ...

    async def user_exists(self, conn: Any, id: uuid.UUID) -> bool: ...

    async def insert_user(
        self,
        conn: Any,
        id: uuid.UUID,
        telegram_user_id: int,
        telegram_chat_id: int,
        username: str | None,
        display_name: str,
        status: str,
        max_subscriptions: int,
        min_subscription_interval_seconds: int,
        last_activity_at: datetime.datetime,
    ) -> None: ...

    def get_users_with_activity_since(
        self,
        conn: Any,
        cutoff_time: datetime.datetime,
    ) -> AsyncIterator[asyncpg.Record]: ...

    def get_users_by_ids(
        self,
        conn: Any,
        user_ids: list[uuid.UUID],
    ) -> AsyncIterator[asyncpg.Record]: ...

    async def update_user_telegram_info(
        self,
        conn: Any,
        telegram_chat_id: int,
        username: str | None,
        display_name: str,
        last_activity_at: datetime.datetime,
        telegram_user_id: int,
    ) -> None: ...

    async def update_user_min_interval(
        self,
        conn: Any,
        min_interval: int,
        user_id: uuid.UUID,
    ) -> None: ...

    async def update_user_max_subscriptions(
        self,
        conn: Any,
        max_subscriptions: int,
        user_id: uuid.UUID,
    ) -> None: ...

    async def update_user_status(
        self,
        conn: Any,
        status: str,
        user_id: uuid.UUID,
    ) -> None: ...

    async def update_user_activity(
        self,
        conn: Any,
        now: datetime.datetime,
        user_id: uuid.UUID,
    ) -> None: ...

    async def system_has_users(
        self,
        conn: Any,
    ) -> None: ...


class TransportQueries(Protocol):
    async def get_provider_by_code(self, conn: Any, code: str) -> asyncpg.Record | None: ...

    async def insert_provider(
        self,
        conn: Any,
        id: uuid.UUID,
        code: str,
        name: str,
        adapter_code: str,
        base_url: str,
        is_active: bool,
    ) -> None: ...

    async def get_stop_by_provider_and_code(
        self, conn: Any, provider_id: uuid.UUID, external_code: str
    ) -> asyncpg.Record | None: ...

    async def insert_stop(
        self,
        conn: Any,
        id: uuid.UUID,
        provider_id: uuid.UUID,
        external_code: str,
        name: str,
        latitude: float | None,
        longitude: float | None,
    ) -> None: ...

    async def update_stop_name(self, conn: Any, name: str, stop_id: uuid.UUID) -> None: ...

    async def get_stop_by_id(self, conn: Any, stop_id: uuid.UUID) -> asyncpg.Record | None: ...

    async def get_route_by_stops(
        self, conn: Any, from_stop_id: uuid.UUID, to_stop_id: uuid.UUID
    ) -> asyncpg.Record | None: ...

    async def insert_route(
        self, conn: Any, id: uuid.UUID, from_stop_id: uuid.UUID, to_stop_id: uuid.UUID
    ) -> None: ...

    async def get_service_by_number_and_route(
        self, conn: Any, external_number: str, route_id: uuid.UUID
    ) -> asyncpg.Record | None: ...

    async def insert_service(
        self,
        conn: Any,
        id: uuid.UUID,
        provider_id: uuid.UUID,
        route_id: uuid.UUID,
        transport_mode: str,
        external_number: str,
        service_type: str,
        days_rule: str,
        days_exceptions: str,
    ) -> None: ...

    async def update_service(
        self,
        conn: Any,
        transport_mode: str,
        service_type: str,
        days_rule: str,
        days_exceptions: str,
        service_id: uuid.UUID,
    ) -> None: ...

    async def get_service_route_by_service_and_route(
        self, conn: Any, service_id: uuid.UUID, route_id: uuid.UUID
    ) -> asyncpg.Record | None: ...

    async def insert_service_route(
        self,
        conn: Any,
        id: uuid.UUID,
        service_id: uuid.UUID,
        route_id: uuid.UUID,
        departure_time: datetime.time | str,
        arrival_time: datetime.time | str,
        duration_minutes: int,
    ) -> None: ...

    async def update_service_route_times(
        self,
        conn: Any,
        departure_time: datetime.time | str,
        arrival_time: datetime.time | str,
        duration_minutes: int,
        service_route_id: uuid.UUID,
    ) -> None: ...

    async def get_service_route_by_id(
        self, conn: Any, service_route_id: uuid.UUID
    ) -> asyncpg.Record | None: ...

    async def get_service_by_id(
        self, conn: Any, service_id: uuid.UUID
    ) -> asyncpg.Record | None: ...

    async def get_route_by_id(self, conn: Any, route_id: uuid.UUID) -> asyncpg.Record | None: ...


class SnapshotsQueries(Protocol):
    async def insert_availability_snapshot(
        self, conn: Any, id: uuid.UUID, subscription_id: uuid.UUID, checked_at: datetime.datetime
    ) -> None: ...

    async def get_latest_snapshot(
        self, conn: Any, subscription_id: uuid.UUID
    ) -> asyncpg.Record | None: ...

    def get_snapshot_seats(
        self, conn: Any, snapshot_id: uuid.UUID
    ) -> AsyncIterator[asyncpg.Record]: ...

    async def insert_snapshot_seat(
        self, conn: Any, snapshot_id: uuid.UUID, unit_type: str, unit_number: str, place_code: str
    ) -> None: ...


class SubscriptionsQueries(Protocol):
    def get_subscriptions_for_user(
        self, conn: Any, user_id: uuid.UUID
    ) -> AsyncIterator[asyncpg.Record]: ...

    def get_all_active_subscriptions(self, conn: Any) -> AsyncIterator[asyncpg.Record]: ...

    async def get_subscription_by_id(
        self, conn: Any, subscription_id: uuid.UUID
    ) -> asyncpg.Record | None: ...

    async def insert_subscription(
        self,
        conn: Any,
        id: uuid.UUID,
        user_id: uuid.UUID,
        service_route_id: uuid.UUID,
        target_date: datetime.date,
        status: str,
        next_check_at: datetime.datetime,
    ) -> None: ...

    async def subscription_exists(
        self,
        conn: Any,
        user_id: uuid.UUID,
        service_route_id: uuid.UUID,
        target_date: datetime.date,
    ) -> bool: ...

    async def get_subscription_count(self, conn: Any, user_id: uuid.UUID) -> int: ...

    async def update_subscription_times(
        self,
        conn: Any,
        subscription_id: uuid.UUID,
        last_checked_at: datetime.datetime | None,
        next_check_at: datetime.datetime | None,
    ) -> None: ...

    async def reset_subscription_check(
        self, conn: Any, subscription_id: uuid.UUID, now: datetime.datetime
    ) -> None: ...

    async def cancel_subscription(self, conn: Any, subscription_id: uuid.UUID) -> None: ...

    def claim_due_subscriptions(
        self, conn: Any, now: datetime.datetime, limit: int
    ) -> AsyncIterator[asyncpg.Record]: ...

    async def update_claimed_subscriptions_next_check(
        self, conn: Any, sub_ids: list[uuid.UUID], next_check_at: datetime.datetime
    ) -> None: ...


class FavoritesQueries(Protocol):
    def get_favorites_for_user(
        self, conn: Any, user_id: uuid.UUID
    ) -> AsyncIterator[asyncpg.Record]: ...

    async def favorite_exists(
        self, conn: Any, user_id: uuid.UUID, service_route_id: uuid.UUID
    ) -> bool: ...

    async def insert_favorite(
        self, conn: Any, id: uuid.UUID, user_id: uuid.UUID, service_route_id: uuid.UUID
    ) -> None: ...

    async def delete_favorite(self, conn: Any, favorite_id: uuid.UUID) -> None: ...


class NotificationsQueries(Protocol):
    async def reset_stuck_processing_notifications(
        self, conn: Any, stuck_cutoff: datetime.datetime
    ) -> None: ...

    def claim_pending_notifications(
        self, conn: Any, now: datetime.datetime, limit: int
    ) -> AsyncIterator[asyncpg.Record]: ...

    async def update_claimed_notifications(
        self, conn: Any, now: datetime.datetime, notification_ids: list[uuid.UUID]
    ) -> None: ...

    def get_notifications_by_ids(
        self, conn: Any, notification_ids: list[uuid.UUID]
    ) -> AsyncIterator[asyncpg.Record]: ...

    async def mark_notification_sent(
        self, conn: Any, now: datetime.datetime, notification_id: uuid.UUID
    ) -> None: ...

    async def mark_notification_failed(
        self,
        conn: Any,
        available_at: datetime.datetime,
        error_text: str,
        notification_id: uuid.UUID,
    ) -> None: ...

    async def insert_notification(
        self,
        conn: Any,
        id: uuid.UUID,
        user_id: uuid.UUID,
        subscription_id: uuid.UUID | None,
        notification_type: str,
        content: str,
        status: str,
        available_at: datetime.datetime,
        attempts: int,
    ) -> None: ...


class MessagesQueries(Protocol):
    async def insert_message(
        self,
        conn: Any,
        id: uuid.UUID,
        sender_user_id: uuid.UUID | None,
        receiver_user_id: uuid.UUID | None,
        content: str,
    ) -> None: ...

    def get_user_messages(self, conn: Any, user_id: uuid.UUID) -> AsyncIterator[asyncpg.Record]: ...

    def get_all_messages(self, conn: Any) -> AsyncIterator[asyncpg.Record]: ...


class BotSessionsQueries(Protocol):
    async def get_conversation_session(
        self, conn: Any, user_id: uuid.UUID
    ) -> asyncpg.Record | None: ...

    async def insert_conversation_session(
        self,
        conn: Any,
        user_id: uuid.UUID,
        current_command_code: int | None,
        last_input_date: datetime.date | None,
        init_state: bool,
        context: str,
        expires_at: datetime.datetime | None,
    ) -> None: ...

    async def update_conversation_session(
        self,
        conn: Any,
        current_command_code: int | None,
        last_input_date: datetime.date | None,
        init_state: bool,
        context: str,
        expires_at: datetime.datetime | None,
        user_id: uuid.UUID,
    ) -> None: ...

    async def delete_conversation_session(self, conn: Any, user_id: uuid.UUID) -> None: ...


class AuditQueries(Protocol):
    async def insert_audit_log(
        self,
        conn: Any,
        id: uuid.UUID,
        actor_user_id: uuid.UUID | None,
        action_code: str,
        entity_schema: str | None,
        entity_table: str | None,
        entity_id: str | None,
        old_values: str | None,
        new_values: str | None,
        source: str,
        correlation_id: uuid.UUID | None,
    ) -> None: ...


UTC = datetime.UTC
MODERATOR_ROLE = "MODERATOR"
DEFAULT_ROLES = (
    (1, "USER", "User"),
    (2, "MODERATOR", "Moderator"),
    (3, "ADMIN", "Administrator"),
)
RW_PROVIDER = {
    "code": "RW_BY",
    "name": "Белорусская железная дорога",
    "adapter_code": "rw_by",
    "base_url": "https://www.rw.by",
}


def _load_queries[QueriesT](filename: str) -> QueriesT:
    import importlib.resources

    sql_text = (
        importlib.resources.files("app.infrastructure.db.queries").joinpath(filename).read_text()
    )
    return aiosql.from_str(sql_text, driver_adapter="asyncpg")


def _now() -> datetime.datetime:
    return datetime.datetime.now(UTC)


def _required_id(value: uuid.UUID | None, entity: str) -> uuid.UUID:
    if value is None:
        raise RuntimeError(f"{entity} id is unexpectedly None")
    return value


def _user_to_entity(row: asyncpg.Record, *, is_moderator: bool) -> User:
    return User(
        id=row["id"],
        telegram_user_id=row["telegram_user_id"],
        telegram_chat_id=row["telegram_chat_id"],
        username=row["username"],
        display_name=row["display_name"],
        is_moderator=is_moderator,
        max_subscriptions=row["max_subscriptions"],
        min_subscriptions_interval=row["min_subscription_interval_seconds"],
        status=row["status"],
        last_activity=row["last_activity_at"],
    )


class _RepositoryBase:
    def __init__(self, pool: ConnectionPool) -> None:
        self._pool = pool


# ---------------------------------------------------------------------------
# Identity: roles
# ---------------------------------------------------------------------------


class RolePostgresRepository(_RepositoryBase):
    async def get_role_id(self, role_code: str) -> int | None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: RolesQueries = _load_queries("roles.sql")
            result = await queries.get_role_id(conn, code=role_code)
            return result if result is not None else None

    async def ensure_default_roles(self) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: RolesQueries = _load_queries("roles.sql")
            existing = [r async for r in queries.get_roles(conn)]
            existing_codes = {row["code"] for row in existing}
            existing_ids = {row["id"] for row in existing}
            next_id = max(existing_ids, default=0) + 1
            for preferred_id, code, name in DEFAULT_ROLES:
                if code in existing_codes:
                    continue
                role_id = preferred_id if preferred_id not in existing_ids else next_id
                if role_id == next_id:
                    next_id += 1
                await queries.insert_role(conn, id=role_id, code=code, name=name)


class UserRolePostgresRepository(_RepositoryBase):
    def __init__(
        self,
        pool: ConnectionPool,
        role_repository: RoleRepository,
    ) -> None:
        super().__init__(pool)
        self._role_repository = role_repository

    async def has_role(self, user_id: uuid.UUID, role_code: str) -> bool:
        role_id = await self._role_repository.get_role_id(role_code)
        if role_id is None:
            return False
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UserRolesQueries = _load_queries("user_roles.sql")
            result = await queries.get_user_role(conn, user_id=user_id, role_id=role_id)
            return result is not None

    async def grant_role(self, user_id: uuid.UUID, role_code: str) -> None:
        await self._role_repository.ensure_default_roles()
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries_roles: RolesQueries = _load_queries("roles.sql")
            role_id = await queries_roles.get_role_id(conn, code=role_code)
            if role_id is None:
                raise KeyError(f"Role {role_code!r} not found")

            queries_users: UsersQueries = _load_queries("users.sql")
            user_exists = await queries_users.user_exists(conn, id=user_id)
            if not user_exists:
                raise KeyError(f"User {user_id} not found")

            queries_user_roles: UserRolesQueries = _load_queries("user_roles.sql")
            existing = await queries_user_roles.get_user_role(
                conn, user_id=user_id, role_id=role_id
            )
            if existing is None:
                await queries_user_roles.insert_user_role(conn, user_id=user_id, role_id=role_id)

    async def revoke_role(self, user_id: uuid.UUID, role_code: str) -> None:
        role_id = await self._role_repository.get_role_id(role_code)
        if role_id is None:
            return
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UserRolesQueries = _load_queries("user_roles.sql")
            await queries.delete_user_role(conn, user_id=user_id, role_id=role_id)

    async def get_user_ids_with_role(self, role_code: str) -> list[uuid.UUID]:
        role_id = await self._role_repository.get_role_id(role_code)
        if role_id is None:
            return []
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UserRolesQueries = _load_queries("user_roles.sql")
            rows = [row async for row in queries.get_user_ids_with_role(conn, role_id=role_id)]
            return [row["user_id"] for row in rows]


# ---------------------------------------------------------------------------
# Identity: users
# ---------------------------------------------------------------------------


class UserPostgresRepository(_RepositoryBase):
    def __init__(
        self,
        pool: ConnectionPool,
        role_repository: UserRoleRepository,
    ) -> None:
        super().__init__(pool)
        self._role_repository = role_repository

    async def register_user(
        self,
        telegram_user_id: int,
        telegram_chat_id: int,
        username: str | None,
        display_name: str,
    ) -> User:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_telegram_id(conn, telegram_user_id=telegram_user_id)
            if row is None:
                user_id = uuid.uuid4()
                await queries.insert_user(
                    conn,
                    id=user_id,
                    telegram_user_id=telegram_user_id,
                    telegram_chat_id=telegram_chat_id,
                    username=username,
                    display_name=display_name,
                    status="ACTIVE",
                    max_subscriptions=5,
                    min_subscription_interval_seconds=15,
                    last_activity_at=_now(),
                )
                row = await queries.get_user_by_id(conn, id=user_id)
            else:
                await queries.update_user_telegram_info(
                    conn,
                    telegram_user_id=telegram_user_id,
                    telegram_chat_id=telegram_chat_id,
                    username=username,
                    display_name=display_name,
                    last_activity_at=_now(),
                )
                row = await queries.get_user_by_telegram_id(conn, telegram_user_id=telegram_user_id)
        if row is None:
            raise KeyError("user is None somehow, we just added it")

        is_moderator = await self._role_repository.has_role(
            _required_id(row["id"], "User"), MODERATOR_ROLE
        )
        return _user_to_entity(row, is_moderator=is_moderator)

    async def is_user_registered(self, user_id: uuid.UUID) -> bool:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            return await queries.user_exists(conn, id=user_id)

    async def add_user(self, user: User) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            await queries.insert_user(
                conn,
                id=user.id,
                telegram_user_id=user.telegram_user_id,
                telegram_chat_id=user.telegram_chat_id,
                display_name=user.display_name,
                username=user.username,
                status=user.status,
                max_subscriptions=user.max_subscriptions,
                min_subscription_interval_seconds=user.min_subscriptions_interval,
                last_activity_at=user.last_activity,
            )

    async def get_user_min_interval(self, user_id: uuid.UUID) -> int:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_id(conn, id=user_id)
            if row is None:
                raise KeyError(f"User {user_id} not found")
            return row["min_subscription_interval_seconds"]

    async def is_user_moderator(self, user_id: uuid.UUID) -> bool:
        return await self._role_repository.has_role(user_id, MODERATOR_ROLE)

    async def get_user_max_subscriptions(self, user_id: uuid.UUID) -> int:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_id(conn, id=user_id)
            if row is None:
                raise KeyError(f"User {user_id} not found")
            return row["max_subscriptions"]

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_id(conn, id=user_id)
            if row is None:
                return None
        is_moderator = await self._role_repository.has_role(user_id, MODERATOR_ROLE)
        return _user_to_entity(row, is_moderator=is_moderator)

    async def set_users_min_interval(self, user_id: uuid.UUID, min_interval: int) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_id(conn, id=user_id)
            if row is None:
                raise KeyError(f"User {user_id} not found")
            await queries.update_user_min_interval(conn, user_id=user_id, min_interval=min_interval)

    async def set_users_max_subscriptions(self, user_id: uuid.UUID, max_subscriptions: int) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_id(conn, id=user_id)
            if row is None:
                raise KeyError(f"User {user_id} not found")
            await queries.update_user_max_subscriptions(
                conn, user_id=user_id, max_subscriptions=max_subscriptions
            )

    async def ban_user(self, user_id: uuid.UUID) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_id(conn, id=user_id)
            if row is None:
                raise KeyError(f"User {user_id} not found")
            await queries.update_user_status(conn, user_id=user_id, status="BLOCKED")

    async def unban_user(self, user_id: uuid.UUID) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_id(conn, id=user_id)
            if row is None:
                raise KeyError(f"User {user_id} not found")
            await queries.update_user_status(conn, user_id=user_id, status="ACTIVE")

    async def promote_user(self, user_id: uuid.UUID) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_id(conn, id=user_id)
            if row is None:
                raise KeyError(f"User {user_id} not found")
        await self._role_repository.grant_role(user_id, MODERATOR_ROLE)

    async def demote_user(self, user_id: uuid.UUID) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_id(conn, id=user_id)
            if row is None:
                raise KeyError(f"User {user_id} not found")
        await self._role_repository.revoke_role(user_id, MODERATOR_ROLE)

    async def is_user_banned(self, user_id: uuid.UUID) -> bool:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            row = await queries.get_user_by_id(conn, id=user_id)
            if row is None:
                raise KeyError(f"User {user_id} not found")
            return row["status"] == "BLOCKED"

    async def update_activity(self, user_id: uuid.UUID) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            await queries.update_user_activity(conn, user_id=user_id, now=_now())

    async def get_last_users(self, time_span: datetime.timedelta) -> list[User]:
        cutoff = _now() - time_span
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            rows = [
                r async for r in queries.get_users_with_activity_since(conn, cutoff_time=cutoff)
            ]
        moderator_ids = set(await self._role_repository.get_user_ids_with_role(MODERATOR_ROLE))
        return [_user_to_entity(row, is_moderator=row["id"] in moderator_ids) for row in rows]

    async def get_moderators(self) -> list[User]:
        moderator_ids = await self._role_repository.get_user_ids_with_role(MODERATOR_ROLE)
        if not moderator_ids:
            return []
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            rows = [r async for r in queries.get_users_by_ids(conn, user_ids=moderator_ids)]
        return [_user_to_entity(row, is_moderator=True) for row in rows]

    async def system_is_empty(self) -> bool:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: UsersQueries = _load_queries("users.sql")
            return not await queries.system_has_users(conn)


# ---------------------------------------------------------------------------
# Transport: normalized service-route aggregate
# ---------------------------------------------------------------------------


class ServiceRoutePostgresRepository(_RepositoryBase):
    async def get_or_create_service_route(self, details: SubscriptionDetails) -> uuid.UUID:
        train = details.train
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries_transport: TransportQueries = _load_queries("transport.sql")
            provider = await queries_transport.get_provider_by_code(conn, code=RW_PROVIDER["code"])
            if provider is None:
                provider_id = uuid.uuid4()
                await queries_transport.insert_provider(
                    conn,
                    id=provider_id,
                    code=RW_PROVIDER["code"],
                    name=RW_PROVIDER["name"],
                    adapter_code=RW_PROVIDER["adapter_code"],
                    base_url=RW_PROVIDER["base_url"],
                    is_active=True,
                )
            else:
                provider_id = provider["id"]

            begin_stop = await self._get_or_create_stop(
                conn,
                queries_transport,
                provider_id=provider_id,
                external_code=train.main_station_from.exp,
                name=train.main_station_from.label,
            )
            end_stop = await self._get_or_create_stop(
                conn,
                queries_transport,
                provider_id=provider_id,
                external_code=train.main_station_to.exp,
                name=train.main_station_to.label,
            )

            full_route_id = await self._get_or_create_route(
                conn, queries_transport, from_stop=begin_stop, to_stop=end_stop
            )

            service_id = await self._get_or_create_service(
                conn,
                queries_transport,
                provider_id=provider_id,
                route_id=full_route_id,
                transport_mode="TRAIN",
                external_number=train.train_number,
                service_type=train.train_type,
                days_rule=train.train_days,
                days_exceptions=train.train_days_except,
            )

            from_stop = await self._get_or_create_stop(
                conn,
                queries_transport,
                provider_id=provider_id,
                external_code=train.station_from.exp,
                name=train.station_from.label,
            )
            to_stop = await self._get_or_create_stop(
                conn,
                queries_transport,
                provider_id=provider_id,
                external_code=train.station_to.exp,
                name=train.station_to.label,
            )

            route_id = await self._get_or_create_route(
                conn, queries_transport, from_stop=from_stop, to_stop=to_stop
            )

            service_route = await queries_transport.get_service_route_by_service_and_route(
                conn, service_id=service_id, route_id=route_id
            )
            if service_route is None:
                service_route_id = uuid.uuid4()
                await queries_transport.insert_service_route(
                    conn,
                    id=service_route_id,
                    service_id=service_id,
                    route_id=route_id,
                    departure_time=train.from_time,
                    arrival_time=train.to_time,
                    duration_minutes=train.duration_minutes,
                )
            else:
                service_route_id = service_route["id"]
                await queries_transport.update_service_route_times(
                    conn,
                    service_route_id=service_route_id,
                    departure_time=train.from_time,
                    arrival_time=train.to_time,
                    duration_minutes=train.duration_minutes,
                )

        return service_route_id

    async def get_train(self, service_route_id: uuid.UUID) -> Train | None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries_transport: TransportQueries = _load_queries("transport.sql")
            service_route = await queries_transport.get_service_route_by_id(
                conn, service_route_id=service_route_id
            )
            if service_route is None:
                return None

            service = await queries_transport.get_service_by_id(
                conn, service_id=service_route["service_id"]
            )
            route = await queries_transport.get_route_by_id(
                conn, route_id=service_route["route_id"]
            )
            if service is None or route is None:
                return None
            main_route = await queries_transport.get_route_by_id(conn, route_id=service["route_id"])
            if main_route is None:
                return None

            from_stop = await queries_transport.get_stop_by_id(conn, stop_id=route["from_stop_id"])
            to_stop = await queries_transport.get_stop_by_id(conn, stop_id=route["to_stop_id"])
            main_from_stop = await queries_transport.get_stop_by_id(
                conn, stop_id=main_route["from_stop_id"]
            )
            main_to_stop = await queries_transport.get_stop_by_id(
                conn, stop_id=main_route["to_stop_id"]
            )
            if (
                from_stop is None
                or to_stop is None
                or main_from_stop is None
                or main_to_stop is None
            ):
                return None

            return Train(
                train_type=service["service_type"] or "p",
                train_number=service["external_number"],
                main_station_from=Station(main_from_stop["name"], main_from_stop["external_code"]),
                main_station_to=Station(main_to_stop["name"], main_to_stop["external_code"]),
                station_from=Station(from_stop["name"], from_stop["external_code"]),
                station_to=Station(to_stop["name"], to_stop["external_code"]),
                from_time=service_route["departure_time"],
                to_time=service_route["arrival_time"],
                train_days=service["days_rule"] or "",
                train_days_except=service["days_exceptions"] or "",
                duration_minutes=service_route["duration_minutes"],
            )

    async def _get_or_create_stop(
        self,
        conn: asyncpg.Connection,
        queries: TransportQueries,
        *,
        provider_id: uuid.UUID,
        external_code: str,
        name: str,
    ) -> uuid.UUID:
        stop = await queries.get_stop_by_provider_and_code(
            conn, provider_id=provider_id, external_code=external_code
        )
        if stop is None:
            stop_id = uuid.uuid4()
            await queries.insert_stop(
                conn,
                id=stop_id,
                provider_id=provider_id,
                external_code=external_code,
                name=name,
                latitude=None,
                longitude=None,
            )
            return stop_id
        else:
            await queries.update_stop_name(conn, name=name, stop_id=stop["id"])
            return stop["id"]

    async def _get_or_create_route(
        self,
        conn: asyncpg.Connection,
        queries: TransportQueries,
        *,
        from_stop: uuid.UUID,
        to_stop: uuid.UUID,
    ) -> uuid.UUID:
        route = await queries.get_route_by_stops(conn, from_stop_id=from_stop, to_stop_id=to_stop)
        if route is None:
            route_id = uuid.uuid4()
            await queries.insert_route(
                conn, id=route_id, from_stop_id=from_stop, to_stop_id=to_stop
            )
            return route_id
        return route["id"]

    async def _get_or_create_service(
        self,
        conn: asyncpg.Connection,
        queries: TransportQueries,
        *,
        provider_id: uuid.UUID,
        route_id: uuid.UUID,
        transport_mode: str,
        external_number: str,
        service_type: str,
        days_rule: str,
        days_exceptions: str,
    ) -> uuid.UUID:
        service = await queries.get_service_by_number_and_route(
            conn, external_number=external_number, route_id=route_id
        )
        if service is None:
            service_id = uuid.uuid4()
            await queries.insert_service(
                conn,
                id=service_id,
                provider_id=provider_id,
                route_id=route_id,
                transport_mode=transport_mode,
                external_number=external_number,
                service_type=service_type,
                days_rule=days_rule,
                days_exceptions=days_exceptions,
            )
            return service_id
        else:
            service_id = service["id"]
            await queries.update_service(
                conn,
                transport_mode=transport_mode,
                service_type=service_type,
                days_rule=days_rule,
                days_exceptions=days_exceptions,
                service_id=service_id,
            )
            return service_id


# ---------------------------------------------------------------------------
# Monitoring: availability snapshots
# ---------------------------------------------------------------------------


class AvailabilitySnapshotPostgresRepository(_RepositoryBase):
    async def save_snapshot(self, subscription_id: uuid.UUID, cars: list[Car]) -> bool:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SnapshotsQueries = _load_queries("snapshots.sql")
            snapshot_id = uuid.uuid4()
            await queries.insert_availability_snapshot(
                conn, id=snapshot_id, subscription_id=subscription_id, checked_at=_now()
            )

            for car in cars:
                for seat in car.free_seats:
                    await queries.insert_snapshot_seat(
                        conn,
                        snapshot_id=snapshot_id,
                        unit_type=str(car.car_type),
                        unit_number=str(car.number),
                        place_code=str(seat),
                    )
        return True

    async def get_latest_snapshot(self, subscription_id: uuid.UUID) -> list[Car]:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SnapshotsQueries = _load_queries("snapshots.sql")
            latest = await queries.get_latest_snapshot(conn, subscription_id=subscription_id)
            if latest is None:
                return []

            seat_rows = [
                row async for row in queries.get_snapshot_seats(conn, snapshot_id=latest["id"])
            ]

        cars_map: dict[tuple[str, str], list[int]] = {}
        for row in seat_rows:
            key = (row["unit_type"], row["unit_number"])
            cars_map.setdefault(key, [])
            with contextlib.suppress(ValueError):
                cars_map[key].append(int(row["place_code"]))

        result: list[Car] = []
        for (unit_type, unit_number), seats in cars_map.items():
            with contextlib.suppress(ValueError):
                result.append(
                    Car(
                        car_type=CarType(int(unit_type)),
                        number=int(unit_number),
                        free_seats=tuple(sorted(seats)),
                    )
                )
        return result


# ---------------------------------------------------------------------------
# Monitoring: subscriptions
# ---------------------------------------------------------------------------


class SubscriptionPostgresRepository(_RepositoryBase):
    def __init__(
        self,
        pool: ConnectionPool,
        service_route_repository: ServiceRouteRepository,
        snapshot_repository: AvailabilitySnapshotRepository,
    ) -> None:
        super().__init__(pool)
        self._service_route_repository = service_route_repository
        self._snapshot_repository = snapshot_repository

    async def get_user_subscriptions(self, user_id: uuid.UUID) -> list[Subscription]:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            rows = [r async for r in queries.get_subscriptions_for_user(conn, user_id=user_id)]
        return [await self._row_to_subscription(row) for row in rows]

    async def get_all_subscriptions(self) -> list[Subscription]:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            rows = [r async for r in queries.get_all_active_subscriptions(conn)]
        return [await self._row_to_subscription(row) for row in rows]

    async def get_by_id(self, subscription_id: uuid.UUID) -> Subscription | None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            row = await queries.get_subscription_by_id(conn, subscription_id=subscription_id)
        return None if row is None else await self._row_to_subscription(row)

    async def add_subscription(self, subscription: Subscription) -> None:
        service_route_id = await self._service_route_repository.get_or_create_service_route(
            subscription.details
        )
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            await queries.insert_subscription(
                conn,
                id=subscription.id,
                user_id=subscription.user_id,
                service_route_id=service_route_id,
                target_date=subscription.details.date,
                status=subscription.status,
                next_check_at=_now(),
            )

    async def remove_subscription(self, subscription: Subscription) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            await queries.cancel_subscription(conn, subscription_id=subscription.id)

    async def subscription_exists(
        self,
        user_id: uuid.UUID,
        service_route_id: uuid.UUID,
        target_date: datetime.date,
    ) -> bool:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            result = await queries.subscription_exists(
                conn, user_id=user_id, service_route_id=service_route_id, target_date=target_date
            )
            return result

    async def get_subscription_count(self, user_id: uuid.UUID) -> int:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            result = await queries.get_subscription_count(conn, user_id=user_id)
            return result

    async def update_subscription(self, subscription: Subscription) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            await queries.update_subscription_times(
                conn,
                subscription_id=subscription.id,
                last_checked_at=subscription.last_checked_at,
                next_check_at=subscription.next_check_at,
            )

    async def reset_subscription(self, subscription: Subscription) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            await queries.reset_subscription_check(
                conn, subscription_id=subscription.id, now=_now()
            )

    async def claim_due_subscriptions(self, limit: int = 10) -> list[Subscription]:
        now = _now()
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            sub_ids = [
                row async for row in queries.claim_due_subscriptions(conn, now=now, limit=limit)
            ]
            sub_ids = [row["id"] for row in sub_ids]
            if not sub_ids:
                return []

            await queries.update_claimed_subscriptions_next_check(
                conn, sub_ids=sub_ids, next_check_at=now + datetime.timedelta(minutes=5)
            )

        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: SubscriptionsQueries = _load_queries("subscriptions.sql")
            rows = []
            for sub_id in sub_ids:
                row = await queries.get_subscription_by_id(conn, subscription_id=sub_id)
                if row is not None:
                    rows.append(row)
        return [await self._row_to_subscription(row) for row in rows]

    async def _row_to_subscription(self, row: asyncpg.Record) -> Subscription:
        subscription_id = row["id"]
        train = await self._service_route_repository.get_train(row["service_route_id"])
        if train is None:
            raise ValueError(f"Invalid service_route data for subscription {subscription_id}")

        details = SubscriptionDetails(train=train, date=row["target_date"])
        last_state = await self._snapshot_repository.get_latest_snapshot(subscription_id)
        return Subscription(
            id=subscription_id,
            user_id=row["user_id"],
            service_route_id=row["service_route_id"],
            target_date=row["target_date"],
            status=row["status"],
            details=details,
            last_checked_at=row["last_checked_at"],
            next_check_at=row["next_check_at"],
            last_state=last_state,
        )


# ---------------------------------------------------------------------------
# Monitoring: favorites
# ---------------------------------------------------------------------------


class FavoritePostgresRepository(_RepositoryBase):
    def __init__(
        self,
        pool: ConnectionPool,
        service_route_repository: ServiceRouteRepository,
    ) -> None:
        super().__init__(pool)
        self._service_route_repository = service_route_repository

    async def get_favorites(self, user_id: uuid.UUID) -> list[Favorite]:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: FavoritesQueries = _load_queries("favorites.sql")
            rows = [r async for r in queries.get_favorites_for_user(conn, user_id=user_id)]

        favorites: list[Favorite] = []
        for row in rows:
            favorite_id = row["id"]
            train = await self._service_route_repository.get_train(row["service_route_id"])
            if train is None:
                raise ValueError(f"Invalid service_route data for favorite {favorite_id}")
            favorites.append(
                Favorite(
                    id=favorite_id,
                    user_id=row["user_id"],
                    train_info=train,
                )
            )
        return favorites

    async def add_favorite(self, favorite: Favorite) -> None:
        service_route_id = await self._service_route_repository.get_or_create_service_route(
            SubscriptionDetails(
                train=favorite.train_info,
                date=datetime.date.today(),
            )
        )
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: FavoritesQueries = _load_queries("favorites.sql")
            await queries.insert_favorite(
                conn, id=favorite.id, user_id=favorite.user_id, service_route_id=service_route_id
            )

    async def remove_favorite(self, favorite: Favorite) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: FavoritesQueries = _load_queries("favorites.sql")
            await queries.delete_favorite(conn, favorite_id=favorite.id)

    async def favorite_exists(self, user_id: uuid.UUID, service_route_id: uuid.UUID) -> bool:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: FavoritesQueries = _load_queries("favorites.sql")
            result = await queries.favorite_exists(
                conn, user_id=user_id, service_route_id=service_route_id
            )
            return result


# ---------------------------------------------------------------------------
# Messaging: transactional outbox
# ---------------------------------------------------------------------------


class NotificationPostgresRepository(_RepositoryBase):
    async def claim_pending_notifications(self, limit: int = 50) -> list[Notification]:
        now = _now()
        stuck_cutoff = now - datetime.timedelta(minutes=5)
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: NotificationsQueries = _load_queries("notifications.sql")
            await queries.reset_stuck_processing_notifications(conn, stuck_cutoff=stuck_cutoff)

            claimed_ids = [
                row async for row in queries.claim_pending_notifications(conn, now=now, limit=limit)
            ]
            claimed_ids = [row["id"] for row in claimed_ids]
            if not claimed_ids:
                return []

            await queries.update_claimed_notifications(conn, now=now, notification_ids=claimed_ids)

            rows = [
                row
                async for row in queries.get_notifications_by_ids(
                    conn, notification_ids=claimed_ids
                )
            ]
            notifications = [
                Notification(
                    id=row["id"],
                    user_id=row["user_id"],
                    content=row["content"],
                    subscription_id=row["subscription_id"],
                    notification_type=row["notification_type"],
                    status=row["status"],
                    attempts=row["attempts"],
                )
                for row in rows
            ]

        return notifications

    async def mark_sent(self, notification_id: uuid.UUID) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: NotificationsQueries = _load_queries("notifications.sql")
            await queries.mark_notification_sent(conn, now=_now(), notification_id=notification_id)

    async def mark_failed(self, notification_id: uuid.UUID, error_text: str) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: NotificationsQueries = _load_queries("notifications.sql")
            queries_result: NotificationsQueries = _load_queries("notifications.sql")
            notif = [
                row
                async for row in queries_result.get_notifications_by_ids(
                    conn, notification_ids=[notification_id]
                )
            ]
            if notif:
                attempts = notif[0]["attempts"]
                available_at = _now() + datetime.timedelta(seconds=10 * (2**attempts))
                await queries.mark_notification_failed(
                    conn,
                    available_at=available_at,
                    error_text=error_text,
                    notification_id=notification_id,
                )

    async def add_notification(self, notification: Notification) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: NotificationsQueries = _load_queries("notifications.sql")
            await queries.insert_notification(
                conn,
                id=notification.id,
                user_id=notification.user_id,
                subscription_id=notification.subscription_id,
                notification_type=notification.notification_type,
                content=notification.content,
                status=notification.status,
                available_at=notification.available_at or _now(),
                attempts=notification.attempts,
            )


# ---------------------------------------------------------------------------
# Messaging: messages
# ---------------------------------------------------------------------------


class MessagePostgresRepository(_RepositoryBase):
    async def add_message(self, message: Message) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: MessagesQueries = _load_queries("messages.sql")
            await queries.insert_message(
                conn,
                id=message.id,
                sender_user_id=message.sender_id,
                receiver_user_id=message.receiver_id,
                content=message.content,
            )

    async def get_user_messages(self, user_id: uuid.UUID) -> list[Message]:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: MessagesQueries = _load_queries("messages.sql")
            rows = [row async for row in queries.get_user_messages(conn, user_id=user_id)]
        return [self._row_to_message(row) for row in rows]

    async def get_all_messages(self) -> list[Message]:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: MessagesQueries = _load_queries("messages.sql")
            rows = [row async for row in queries.get_all_messages(conn)]
        return [self._row_to_message(row) for row in rows]

    @staticmethod
    def _row_to_message(row: asyncpg.Record) -> Message:
        return Message(
            id=row["id"],
            sender_id=row["sender_user_id"],
            receiver_id=row["receiver_user_id"],
            content=row["content"],
            sent_date=row["sent_at"],
        )


# ---------------------------------------------------------------------------
# Bot state
# ---------------------------------------------------------------------------


class ConversationSessionPostgresRepository(_RepositoryBase):
    async def get(self, user_id: uuid.UUID) -> dict[str, object] | None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: BotSessionsQueries = _load_queries("bot_sessions.sql")
            row = await queries.get_conversation_session(conn, user_id=user_id)
            if row is None:
                return None
            return {
                "user_id": row["user_id"],
                "current_command_code": row["current_command_code"],
                "last_input_date": row["last_input_date"],
                "init_state": row["init_state"],
                "context": dict(row["context"]),
                "expires_at": row["expires_at"],
                "updated_at": row["updated_at"],
            }

    async def save(
        self,
        *,
        user_id: uuid.UUID,
        current_command_code: int | None,
        last_input_date: datetime.date | None,
        init_state: bool,
        context: dict[str, Any],
        expires_at: datetime.datetime | None,
    ) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: BotSessionsQueries = _load_queries("bot_sessions.sql")
            row = await queries.get_conversation_session(conn, user_id=user_id)
            if row is None:
                await queries.insert_conversation_session(
                    conn,
                    user_id=user_id,
                    current_command_code=current_command_code,
                    last_input_date=last_input_date,
                    init_state=init_state,
                    context=json.dumps(context),
                    expires_at=expires_at,
                )
            else:
                await queries.update_conversation_session(
                    conn,
                    user_id=user_id,
                    current_command_code=current_command_code,
                    last_input_date=last_input_date,
                    init_state=init_state,
                    context=json.dumps(context),
                    expires_at=expires_at,
                )

    async def delete(self, user_id: uuid.UUID) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: BotSessionsQueries = _load_queries("bot_sessions.sql")
            await queries.delete_conversation_session(conn, user_id=user_id)


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------


class AuditLogPostgresRepository(_RepositoryBase):
    async def add(
        self,
        *,
        actor_user_id: uuid.UUID | None,
        action_code: str,
        entity_schema: str | None = None,
        entity_table: str | None = None,
        entity_id: str | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
        correlation_id: uuid.UUID | None = None,
        source: str = "BOT",
    ) -> None:
        async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries: AuditQueries = _load_queries("audit.sql")
            await queries.insert_audit_log(
                conn,
                id=uuid.uuid4(),
                actor_user_id=actor_user_id,
                action_code=action_code,
                entity_schema=entity_schema,
                entity_table=entity_table,
                entity_id=entity_id,
                old_values=json.dumps(old_values) if old_values else None,
                new_values=json.dumps(new_values) if new_values else None,
                correlation_id=correlation_id,
                source=source,
            )
