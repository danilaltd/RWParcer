"""PostgreSQL repositories for the application domain.

Repositories are organized by domain responsibility rather than by how many ORM
rows happen to participate in an operation. The transport service-route repository
owns the normalized transport aggregate, while monitoring, messaging, bot state and
audit storage each have their own repository.
"""

from __future__ import annotations

import contextlib
import datetime
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import delete, exists, func, select, update

from app.domain.entities import Favorite, Message, Notification, Subscription, User
from app.domain.value_objects import Car, CarType, Station, SubscriptionDetails, Train
from app.infrastructure.db.models import (
    AuditLogRow,
    AvailabilitySnapshotRow,
    AvailabilitySnapshotSeatRow,
    ConversationSessionRow,
    FavoriteRow,
    MessageRow,
    NotificationRow,
    ProviderRow,
    RoleRow,
    RouteRow,
    ServiceRouteRow,
    ServiceRow,
    StopRow,
    SubscriptionRow,
    UserRoleRow,
    UserRow,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from app.domain.protocols import (
        AvailabilitySnapshotRepository,
        RoleRepository,
        ServiceRouteRepository,
        UserRoleRepository,
    )


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


class _RepositoryBase:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory


def _required_id(value: uuid.UUID | None, entity: str) -> uuid.UUID:
    if value is None:
        raise RuntimeError(f"{entity} id is unexpectedly None")
    return value


def _now() -> datetime.datetime:
    return datetime.datetime.now(UTC)


def _user_to_entity(row: UserRow, *, is_moderator: bool) -> User:
    return User(
        id=_required_id(row.id, "User"),
        telegram_user_id=row.telegram_user_id,
        telegram_chat_id=row.telegram_chat_id,
        username=row.username,
        display_name=row.display_name,
        is_moderator=is_moderator,
        max_subscriptions=row.max_subscriptions,
        min_subscriptions_interval=row.min_subscription_interval_seconds,
        status=row.status,
        last_activity=row.last_activity_at,
    )


# ---------------------------------------------------------------------------
# Identity: roles
# ---------------------------------------------------------------------------


class RolePostgresRepository(_RepositoryBase):
    async def get_role_id(self, role_code: str) -> int | None:
        async with self._session_factory() as session:
            return await session.scalar(select(RoleRow.id).where(RoleRow.code == role_code))

    async def ensure_default_roles(self) -> None:
        async with self._session_factory() as session:
            existing = list(await session.scalars(select(RoleRow)))
            existing_codes = {role.code for role in existing}
            existing_ids = {role.id for role in existing}
            next_id = max(existing_ids, default=0) + 1
            for preferred_id, code, name in DEFAULT_ROLES:
                if code in existing_codes:
                    continue
                role_id = preferred_id if preferred_id not in existing_ids else next_id
                if role_id == next_id:
                    next_id += 1
                session.add(RoleRow(id=role_id, code=code, name=name))
            await session.commit()


class UserRolePostgresRepository(_RepositoryBase):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        role_repository: RoleRepository,
    ) -> None:
        super().__init__(session_factory)
        self._role_repository = role_repository

    async def has_role(self, user_id: uuid.UUID, role_code: str) -> bool:
        role_id = await self._role_repository.get_role_id(role_code)
        if role_id is None:
            return False
        async with self._session_factory() as session:
            return (
                await session.scalar(
                    select(UserRoleRow.user_id)
                    .where(
                        UserRoleRow.user_id == user_id,
                        UserRoleRow.role_id == role_id,
                    )
                    .limit(1)
                )
            ) is not None

    async def grant_role(self, user_id: uuid.UUID, role_code: str) -> None:
        await self._role_repository.ensure_default_roles()
        async with self._session_factory() as session:
            role_id = await self._role_repository.get_role_id(role_code)
            if role_id is None:
                raise KeyError(f"Role {role_code!r} not found")

            user_exists = await session.scalar(select(exists().where(UserRow.id == user_id)))
            if not user_exists:
                raise KeyError(f"User {user_id} not found")

            existing = await session.scalar(
                select(UserRoleRow).where(
                    UserRoleRow.user_id == user_id,
                    UserRoleRow.role_id == role_id,
                )
            )
            if existing is None:
                session.add(UserRoleRow(user_id=user_id, role_id=role_id))
            await session.commit()

    async def revoke_role(self, user_id: uuid.UUID, role_code: str) -> None:
        role_id = await self._role_repository.get_role_id(role_code)
        if role_id is None:
            return
        async with self._session_factory() as session:
            await session.execute(
                delete(UserRoleRow).where(
                    UserRoleRow.user_id == user_id,
                    UserRoleRow.role_id == role_id,
                )
            )
            await session.commit()

    async def get_user_ids_with_role(self, role_code: str) -> list[uuid.UUID]:
        role_id = await self._role_repository.get_role_id(role_code)
        if role_id is None:
            return []
        async with self._session_factory() as session:
            rows = await session.scalars(
                select(UserRoleRow.user_id).where(UserRoleRow.role_id == role_id)
            )
            return list(rows)


# ---------------------------------------------------------------------------
# Identity: users
# ---------------------------------------------------------------------------


class UserPostgresRepository(_RepositoryBase):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        role_repository: UserRoleRepository,
    ) -> None:
        super().__init__(session_factory)
        self._role_repository = role_repository

    async def register_user(
        self,
        telegram_user_id: int,
        telegram_chat_id: int,
        username: str | None,
        display_name: str,
    ) -> User:
        async with self._session_factory() as session:
            row = await session.scalar(
                select(UserRow).where(UserRow.telegram_user_id == telegram_user_id)
            )
            if row is None:
                row = UserRow(
                    id=uuid.uuid4(),
                    telegram_user_id=telegram_user_id,
                    telegram_chat_id=telegram_chat_id,
                    username=username,
                    display_name=display_name,
                    status="ACTIVE",
                    max_subscriptions=5,
                    min_subscription_interval_seconds=15,
                    last_activity_at=_now(),
                )
                session.add(row)
            else:
                row.telegram_chat_id = telegram_chat_id
                row.username = username
                row.display_name = display_name
                row.last_activity_at = _now()

            await session.commit()
            await session.refresh(row)

        is_moderator = await self._role_repository.has_role(
            _required_id(row.id, "User"), MODERATOR_ROLE
        )
        return _user_to_entity(row, is_moderator=is_moderator)

    async def is_user_registered(self, user_id: uuid.UUID) -> bool:
        async with self._session_factory() as session:
            return bool(await session.scalar(select(exists().where(UserRow.id == user_id))))

    async def add_user(self, user: User) -> None:
        async with self._session_factory() as session:
            session.add(
                UserRow(
                    id=user.id,
                    telegram_user_id=user.telegram_user_id,
                    telegram_chat_id=user.telegram_chat_id,
                    username=user.username,
                    display_name=user.display_name,
                    status=user.status,
                    max_subscriptions=user.max_subscriptions,
                    min_subscription_interval_seconds=user.min_subscriptions_interval,
                    last_activity_at=user.last_activity,
                )
            )
            await session.commit()

    async def get_user_min_interval(self, user_id: uuid.UUID) -> int:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            return row.min_subscription_interval_seconds

    async def is_user_moderator(self, user_id: uuid.UUID) -> bool:
        return await self._role_repository.has_role(user_id, MODERATOR_ROLE)

    async def get_user_max_subscriptions(self, user_id: uuid.UUID) -> int:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            return row.max_subscriptions

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        async with self._session_factory() as session:
            row = await session.scalar(select(UserRow).where(UserRow.id == user_id))
            if row is None:
                return None
        return _user_to_entity(
            row,
            is_moderator=await self._role_repository.has_role(user_id, MODERATOR_ROLE),
        )

    async def set_users_min_interval(self, user_id: uuid.UUID, min_interval: int) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.min_subscription_interval_seconds = min_interval
            await session.commit()

    async def set_users_max_subscriptions(self, user_id: uuid.UUID, max_subscriptions: int) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.max_subscriptions = max_subscriptions
            await session.commit()

    async def ban_user(self, user_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.status = "BLOCKED"
            await session.commit()

    async def unban_user(self, user_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.status = "ACTIVE"
            await session.commit()

    async def promote_user(self, user_id: uuid.UUID) -> None:
        await self._user_or_raise_by_id(user_id)
        await self._role_repository.grant_role(user_id, MODERATOR_ROLE)

    async def demote_user(self, user_id: uuid.UUID) -> None:
        await self._user_or_raise_by_id(user_id)
        await self._role_repository.revoke_role(user_id, MODERATOR_ROLE)

    async def is_user_banned(self, user_id: uuid.UUID) -> bool:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            return row.status == "BLOCKED"

    async def update_activity(self, user_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            row = await session.scalar(select(UserRow).where(UserRow.id == user_id))
            if row is not None:
                row.last_activity_at = _now()
                await session.commit()

    async def get_last_users(self, time_span: datetime.timedelta) -> list[User]:
        cutoff = _now() - time_span
        async with self._session_factory() as session:
            rows = list(
                await session.scalars(select(UserRow).where(UserRow.last_activity_at >= cutoff))
            )
        moderator_ids = set(await self._role_repository.get_user_ids_with_role(MODERATOR_ROLE))
        return [
            _user_to_entity(row, is_moderator=_required_id(row.id, "User") in moderator_ids)
            for row in rows
        ]

    async def get_moderators(self) -> list[User]:
        moderator_ids = await self._role_repository.get_user_ids_with_role(MODERATOR_ROLE)
        if not moderator_ids:
            return []
        async with self._session_factory() as session:
            rows = list(await session.scalars(select(UserRow).where(UserRow.id.in_(moderator_ids))))
        return [_user_to_entity(row, is_moderator=True) for row in rows]

    async def _user_or_raise(self, session: AsyncSession, user_id: uuid.UUID) -> UserRow:
        row = await session.scalar(select(UserRow).where(UserRow.id == user_id))
        if row is None:
            raise KeyError(f"User {user_id} not found")
        return row

    async def _user_or_raise_by_id(self, user_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            await self._user_or_raise(session, user_id)


# ---------------------------------------------------------------------------
# Transport: normalized service-route aggregate
# ---------------------------------------------------------------------------


class ServiceRoutePostgresRepository(_RepositoryBase):
    """Persist and reconstruct a transport service-route aggregate.

    Provider/stop/route/service rows are normalized storage details of this aggregate;
    callers should not have to coordinate five different repositories for one route.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        super().__init__(session_factory)

    async def get_or_create_service_route(self, details: SubscriptionDetails) -> uuid.UUID:
        train = details.train
        async with self._session_factory() as session:
            provider = await session.scalar(
                select(ProviderRow).where(ProviderRow.code == RW_PROVIDER["code"])
            )
            if provider is None:
                provider = ProviderRow(
                    id=uuid.uuid4(),
                    code=RW_PROVIDER["code"],
                    name=RW_PROVIDER["name"],
                    adapter_code=RW_PROVIDER["adapter_code"],
                    base_url=RW_PROVIDER["base_url"],
                    is_active=True,
                )
                session.add(provider)
                await session.flush()

            provider_id = _required_id(provider.id, "Provider")
            begin_stop = await self._get_or_create_stop(
                session,
                provider_id=provider_id,
                external_code=train.main_station_from.exp,
                name=train.main_station_from.label,
            )
            end_stop = await self._get_or_create_stop(
                session,
                provider_id=provider_id,
                external_code=train.main_station_to.exp,
                name=train.main_station_to.label,
            )

            full_route_id = await self._get_or_create_route(
                session, from_stop=begin_stop, to_stop=end_stop
            )

            service_id = await self._get_or_create_service(
                session,
                provider_id=provider_id,
                route_id=full_route_id,
                transport_mode="TRAIN",
                external_number=train.train_number,
                service_type=train.train_type,
                days_rule=train.train_days,
                days_exceptions=train.train_days_except,
            )

            from_stop = await self._get_or_create_stop(
                session,
                provider_id=provider_id,
                external_code=train.station_from.exp,
                name=train.station_from.label,
            )
            to_stop = await self._get_or_create_stop(
                session,
                provider_id=provider_id,
                external_code=train.station_to.exp,
                name=train.station_to.label,
            )

            route_id = await self._get_or_create_route(
                session, from_stop=from_stop, to_stop=to_stop
            )

            service_route = await session.scalar(
                select(ServiceRouteRow).where(
                    ServiceRouteRow.service_id == service_id,
                    ServiceRouteRow.route_id == route_id,
                )
            )
            if service_route is None:
                service_route = ServiceRouteRow(
                    id=uuid.uuid4(),
                    service_id=service_id,
                    route_id=route_id,
                    departure_time=train.from_time,
                    arrival_time=train.to_time,
                    duration_minutes=train.duration_minutes,
                )
                session.add(service_route)
            else:
                service_route.departure_time = train.from_time
                service_route.arrival_time = train.to_time
                service_route.duration_minutes = train.duration_minutes

            await session.commit()
            service_route_id = _required_id(service_route.id, "ServiceRoute")

        return service_route_id

    async def get_train(self, service_route_id: uuid.UUID) -> Train | None:
        async with self._session_factory() as session:
            service_route = await session.scalar(
                select(ServiceRouteRow).where(ServiceRouteRow.id == service_route_id)
            )
            if service_route is None:
                return None

            service = await session.get(ServiceRow, service_route.service_id)
            route = await session.get(RouteRow, service_route.route_id)
            main_route = await session.get(RouteRow, service.route_id)
            if service is None or route is None:
                return None

            from_stop = await session.get(StopRow, route.from_stop_id)
            to_stop = await session.get(StopRow, route.to_stop_id)
            main_from_stop = await session.get(StopRow, main_route.from_stop_id)
            main_to_stop = await session.get(StopRow, main_route.to_stop_id)
            if from_stop is None or to_stop is None or main_from_stop is None or main_to_stop is None:
                return None

            return Train(
                train_type=service.service_type or "p",
                train_number=service.external_number,
                main_station_from=Station(main_from_stop.name, main_from_stop.external_code),
                main_station_to=Station(main_to_stop.name, main_to_stop.external_code),
                station_from=Station(from_stop.name, from_stop.external_code),
                station_to=Station(to_stop.name, to_stop.external_code),
                from_time=service_route.departure_time,
                to_time=service_route.arrival_time,
                train_days=service.days_rule or "",
                train_days_except=service.days_exceptions or "",
                duration_minutes=service_route.duration_minutes,
            )

    async def _get_or_create_stop(
        self,
        session: AsyncSession,
        *,
        provider_id: uuid.UUID,
        external_code: str,
        name: str,
    ) -> uuid.UUID:
        stop = await session.scalar(
            select(StopRow).where(
                StopRow.provider_id == provider_id,
                StopRow.external_code == external_code,
            )
        )
        if stop is None:
            stop = StopRow(
                id=uuid.uuid4(),
                provider_id=provider_id,
                external_code=external_code,
                name=name,
                # todo: fetch coordinates from provider API if available
                latitude=None,
                longitude=None,
            )
            session.add(stop)
        else:
            stop.name = name
        await session.flush()
        return _required_id(stop.id, "Stop")

    async def _get_or_create_route(
        self,
        session: AsyncSession,
        *,
        from_stop: uuid.UUID,
        to_stop: uuid.UUID,
    ) -> uuid.UUID:
        route = await session.scalar(
            select(RouteRow).where(
                RouteRow.from_stop_id == from_stop,
                RouteRow.to_stop_id == to_stop,
            )
        )
        if route is None:
            route = RouteRow(
                id=uuid.uuid4(),
                from_stop_id=from_stop,
                to_stop_id=to_stop,
            )
            session.add(route)
            await session.flush()
        return _required_id(route.id, "Route")

    async def _get_or_create_service(
        self,
        session: AsyncSession,
        *,
        provider_id: uuid.UUID,
        route_id: uuid.UUID,
        transport_mode: str,
        external_number: str,
        service_type: str,
        days_rule: str,
        days_exceptions: str,
    ) -> uuid.UUID:
        service = await session.scalar(
            select(ServiceRow).where(
                ServiceRow.external_number == external_number,
                ServiceRow.route_id == route_id,
            )
        )
        if service is None:
            service = ServiceRow(
                provider_id=provider_id,
                route_id=route_id,
                transport_mode=transport_mode,
                external_number=external_number,
                service_type=service_type,
                days_rule=days_rule,
                days_exceptions=days_exceptions,
            )
            session.add(service)
        else:
            service.transport_mode = transport_mode
            service.service_type = service_type
            service.days_rule = days_rule
            service.days_exceptions = days_exceptions
        await session.flush()
        return _required_id(service.id, "Service")


# ---------------------------------------------------------------------------
# Monitoring: availability snapshots
# ---------------------------------------------------------------------------


class AvailabilitySnapshotPostgresRepository(_RepositoryBase):
    async def save_snapshot(self, subscription_id: uuid.UUID, cars: list[Car]) -> bool:
        async with self._session_factory() as session:
            snapshot = AvailabilitySnapshotRow(
                id=uuid.uuid4(),
                subscription_id=subscription_id,
                checked_at=_now(),
            )
            session.add(snapshot)
            snapshot_id = _required_id(snapshot.id, "AvailabilitySnapshot")

            for car in cars:
                for seat in car.free_seats:
                    session.add(
                        AvailabilitySnapshotSeatRow(
                            snapshot_id=snapshot_id,
                            unit_type=str(car.car_type),
                            unit_number=str(car.number),
                            place_code=str(seat),
                        )
                    )
            await session.commit()
        return True

    async def get_latest_snapshot(self, subscription_id: uuid.UUID) -> list[Car]:
        async with self._session_factory() as session:
            latest = await session.scalar(
                select(AvailabilitySnapshotRow)
                .where(AvailabilitySnapshotRow.subscription_id == subscription_id)
                .order_by(AvailabilitySnapshotRow.checked_at.desc())
                .limit(1)
            )
            if latest is None:
                return []

            seat_rows = list(
                await session.scalars(
                    select(AvailabilitySnapshotSeatRow).where(
                        AvailabilitySnapshotSeatRow.snapshot_id == latest.id
                    )
                )
            )

        cars_map: dict[tuple[str, str], list[int]] = {}
        for row in seat_rows:
            key = (row.unit_type, row.unit_number)
            cars_map.setdefault(key, [])
            with contextlib.suppress(ValueError):
                cars_map[key].append(int(row.place_code))

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
        session_factory: async_sessionmaker[AsyncSession],
        service_route_repository: ServiceRouteRepository,
        snapshot_repository: AvailabilitySnapshotRepository,
    ) -> None:
        super().__init__(session_factory)
        self._service_route_repository = service_route_repository
        self._snapshot_repository = snapshot_repository

    async def get_user_subscriptions(self, user_id: uuid.UUID) -> list[Subscription]:
        async with self._session_factory() as session:
            rows = list(
                await session.scalars(
                    select(SubscriptionRow).where(
                        SubscriptionRow.user_id == user_id,
                        SubscriptionRow.status.in_(["ACTIVE", "PAUSED"]),
                    )
                )
            )
        return [await self._row_to_subscription(row) for row in rows]

    async def get_all_subscriptions(self) -> list[Subscription]:
        async with self._session_factory() as session:
            rows = list(
                await session.scalars(
                    select(SubscriptionRow).where(SubscriptionRow.status.in_(["ACTIVE", "PAUSED"]))
                )
            )
        return [await self._row_to_subscription(row) for row in rows]

    async def get_by_id(self, subscription_id: uuid.UUID) -> Subscription | None:
        async with self._session_factory() as session:
            row = await session.scalar(
                select(SubscriptionRow).where(SubscriptionRow.id == subscription_id)
            )
        return None if row is None else await self._row_to_subscription(row)

    async def add_subscription(self, subscription: Subscription) -> None:
        service_route_id = await self._service_route_repository.get_or_create_service_route(
            subscription.details
        )
        async with self._session_factory() as session:
            session.add(
                SubscriptionRow(
                    id=subscription.id,
                    user_id=subscription.user_id,
                    service_route_id=service_route_id,
                    target_date=subscription.details.date,
                    status=subscription.status,
                    next_check_at=_now(),
                )
            )
            await session.commit()

    async def remove_subscription(self, subscription: Subscription) -> None:
        async with self._session_factory() as session:
            row = await session.get(SubscriptionRow, subscription.id)
            if row is not None:
                row.status = "CANCELLED"
                await session.commit()

    async def subscription_exists(
        self,
        user_id: uuid.UUID,
        service_route_id: uuid.UUID,
        target_date: datetime.date,
    ) -> bool:
        async with self._session_factory() as session:
            count = await session.scalar(
                select(func.count())
                .select_from(SubscriptionRow)
                .where(
                    SubscriptionRow.user_id == user_id,
                    SubscriptionRow.service_route_id == service_route_id,
                    SubscriptionRow.target_date == target_date,
                    SubscriptionRow.status.in_(["ACTIVE", "PAUSED"]),
                )
            )
            return int(count or 0) > 0

    async def get_subscription_count(self, user_id: uuid.UUID) -> int:
        async with self._session_factory() as session:
            count = await session.scalar(
                select(func.count())
                .select_from(SubscriptionRow)
                .where(
                    SubscriptionRow.user_id == user_id,
                    SubscriptionRow.status.in_(["ACTIVE", "PAUSED"]),
                )
            )
            return int(count or 0)

    async def update_subscription(self, subscription: Subscription) -> None:
        async with self._session_factory() as session:
            row = await session.get(SubscriptionRow, subscription.id)
            if row is not None:
                row.last_checked_at = subscription.last_checked_at
                row.next_check_at = subscription.next_check_at
                await session.commit()

    async def reset_subscription(self, subscription: Subscription) -> None:
        async with self._session_factory() as session:
            row = await session.get(SubscriptionRow, subscription.id)
            if row is not None:
                row.next_check_at = _now()
                await session.commit()

    async def claim_due_subscriptions(self, limit: int = 10) -> list[Subscription]:
        now = _now()
        async with self._session_factory() as session:
            sub_ids = (
                await session.scalars(
                    select(SubscriptionRow.id)
                    .where(
                        SubscriptionRow.status == "ACTIVE",
                        (SubscriptionRow.next_check_at.is_(None))
                        | (SubscriptionRow.next_check_at <= now),
                    )
                    .order_by(SubscriptionRow.next_check_at, SubscriptionRow.id)
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                )
            ).all()
            sub_ids = [value for value in sub_ids if value is not None]
            if not sub_ids:
                await session.commit()
                return []

            await session.execute(
                update(SubscriptionRow)
                .where(SubscriptionRow.id.in_(sub_ids))
                .values(next_check_at=now + datetime.timedelta(minutes=5))
            )
            await session.commit()

        async with self._session_factory() as session:
            rows = list(
                await session.scalars(
                    select(SubscriptionRow).where(SubscriptionRow.id.in_(sub_ids))
                )
            )
        return [await self._row_to_subscription(row) for row in rows]

    async def _row_to_subscription(self, row: SubscriptionRow) -> Subscription:
        subscription_id = _required_id(row.id, "Subscription")
        train = await self._service_route_repository.get_train(row.service_route_id)
        if train is None:
            raise ValueError(f"Invalid service_route data for subscription {subscription_id}")

        details = SubscriptionDetails(train=train, date=row.target_date)
        last_state = await self._snapshot_repository.get_latest_snapshot(subscription_id)
        return Subscription(
            id=subscription_id,
            user_id=row.user_id,
            service_route_id=row.service_route_id,
            target_date=row.target_date,
            status=row.status,
            details=details,
            last_checked_at=row.last_checked_at,
            next_check_at=row.next_check_at,
            last_state=last_state,
        )


# ---------------------------------------------------------------------------
# Monitoring: favorites
# ---------------------------------------------------------------------------


class FavoritePostgresRepository(_RepositoryBase):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        service_route_repository: ServiceRouteRepository,
    ) -> None:
        super().__init__(session_factory)
        self._service_route_repository = service_route_repository

    async def get_favorites(self, user_id: uuid.UUID) -> list[Favorite]:
        async with self._session_factory() as session:
            rows = list(
                await session.scalars(select(FavoriteRow).where(FavoriteRow.user_id == user_id))
            )

        favorites: list[Favorite] = []
        for row in rows:
            favorite_id = _required_id(row.id, "Favorite")
            train = await self._service_route_repository.get_train(row.service_route_id)
            if train is None:
                raise ValueError(f"Invalid service_route data for favorite {favorite_id}")
            favorites.append(
                Favorite(
                    id=favorite_id,
                    user_id=row.user_id,
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
        async with self._session_factory() as session:
            session.add(
                FavoriteRow(
                    id=favorite.id,
                    user_id=favorite.user_id,
                    service_route_id=service_route_id,
                )
            )
            await session.commit()

    async def remove_favorite(self, favorite: Favorite) -> None:
        async with self._session_factory() as session:
            await session.execute(delete(FavoriteRow).where(FavoriteRow.id == favorite.id))
            await session.commit()

    async def favorite_exists(self, user_id: uuid.UUID, service_route_id: uuid.UUID) -> bool:
        async with self._session_factory() as session:
            count = await session.scalar(
                select(func.count())
                .select_from(FavoriteRow)
                .where(
                    FavoriteRow.user_id == user_id,
                    FavoriteRow.service_route_id == service_route_id,
                )
            )
            return int(count or 0) > 0


# ---------------------------------------------------------------------------
# Messaging: transactional outbox
# ---------------------------------------------------------------------------


class NotificationPostgresRepository(_RepositoryBase):
    async def claim_pending_notifications(self, limit: int = 50) -> list[Notification]:
        now = _now()
        stuck_cutoff = now - datetime.timedelta(minutes=5)
        async with self._session_factory() as session:
            await session.execute(
                update(NotificationRow)
                .where(
                    NotificationRow.status == "PROCESSING",
                    NotificationRow.locked_at <= stuck_cutoff,
                )
                .values(status="PENDING", locked_at=None)
            )

            claimed_ids = (
                await session.scalars(
                    select(NotificationRow.id)
                    .where(
                        NotificationRow.status == "PENDING",
                        NotificationRow.available_at <= now,
                        NotificationRow.attempts < 5,
                    )
                    .order_by(NotificationRow.available_at, NotificationRow.id)
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                )
            ).all()
            claimed_ids = [value for value in claimed_ids if value is not None]
            if not claimed_ids:
                await session.commit()
                return []

            await session.execute(
                update(NotificationRow)
                .where(NotificationRow.id.in_(claimed_ids))
                .values(
                    status="PROCESSING",
                    locked_at=now,
                    attempts=NotificationRow.attempts + 1,
                )
            )
            rows = list(
                await session.scalars(
                    select(NotificationRow).where(NotificationRow.id.in_(claimed_ids))
                )
            )
            notifications = [
                Notification(
                    id=_required_id(row.id, "Notification"),
                    user_id=row.user_id,
                    content=row.content,
                    subscription_id=row.subscription_id,
                    notification_type=row.notification_type,
                    status=row.status,
                    attempts=row.attempts,
                )
                for row in rows
            ]
            await session.commit()

        return notifications

    async def mark_sent(self, notification_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            row = await session.get(NotificationRow, notification_id)
            if row is not None:
                row.status = "SENT"
                row.sent_at = _now()
                row.locked_at = None
                await session.commit()

    async def mark_failed(self, notification_id: uuid.UUID, error_text: str) -> None:
        async with self._session_factory() as session:
            row = await session.get(NotificationRow, notification_id)
            if row is not None:
                row.status = "PENDING"
                row.available_at = _now() + datetime.timedelta(seconds=10 * (2**row.attempts))
                row.locked_at = None
                row.last_error = error_text
                await session.commit()

    async def add_notification(self, notification: Notification) -> None:
        async with self._session_factory() as session:
            session.add(
                NotificationRow(
                    id=notification.id,
                    user_id=notification.user_id,
                    subscription_id=notification.subscription_id,
                    notification_type=notification.notification_type,
                    content=notification.content,
                    status=notification.status,
                    available_at=notification.available_at or _now(),
                    attempts=notification.attempts,
                )
            )
            await session.commit()


# ---------------------------------------------------------------------------
# Messaging: messages
# ---------------------------------------------------------------------------


class MessagePostgresRepository(_RepositoryBase):
    async def add_message(self, message: Message) -> None:
        async with self._session_factory() as session:
            session.add(
                MessageRow(
                    id=message.id,
                    sender_user_id=message.sender_id,
                    receiver_user_id=message.receiver_id,
                    content=message.content,
                )
            )
            await session.commit()

    async def get_user_messages(self, user_id: uuid.UUID) -> list[Message]:
        async with self._session_factory() as session:
            rows = list(
                await session.scalars(
                    select(MessageRow)
                    .where(
                        (MessageRow.receiver_user_id == user_id)
                        | (MessageRow.sender_user_id == user_id)
                    )
                    .order_by(MessageRow.sent_at)
                )
            )
        return [self._row_to_message(row) for row in rows]

    async def get_all_messages(self) -> list[Message]:
        async with self._session_factory() as session:
            rows = list(await session.scalars(select(MessageRow).order_by(MessageRow.sent_at)))
        return [self._row_to_message(row) for row in rows]

    @staticmethod
    def _row_to_message(row: MessageRow) -> Message:
        return Message(
            id=_required_id(row.id, "Message"),
            sender_id=row.sender_user_id,
            receiver_id=row.receiver_user_id,
            content=row.content,
            sent_date=row.sent_at,
        )


# ---------------------------------------------------------------------------
# Bot state
# ---------------------------------------------------------------------------


class ConversationSessionPostgresRepository(_RepositoryBase):
    async def get(self, user_id: uuid.UUID) -> dict[str, object] | None:
        async with self._session_factory() as session:
            row = await session.get(ConversationSessionRow, user_id)
            if row is None:
                return None
            return {
                "user_id": row.user_id,
                "current_command_code": row.current_command_code,
                "last_input_date": row.last_input_date,
                "init_state": row.init_state,
                "context": dict(row.context),
                "expires_at": row.expires_at,
                "updated_at": row.updated_at,
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
        async with self._session_factory() as session:
            row = await session.get(ConversationSessionRow, user_id)
            if row is None:
                row = ConversationSessionRow(
                    user_id=user_id,
                    current_command_code=current_command_code,
                    last_input_date=last_input_date,
                    init_state=init_state,
                    context=context,
                    expires_at=expires_at,
                )
                session.add(row)
            else:
                row.current_command_code = current_command_code
                row.last_input_date = last_input_date
                row.init_state = init_state
                row.context = context
                row.expires_at = expires_at
            await session.commit()

    async def delete(self, user_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ConversationSessionRow).where(ConversationSessionRow.user_id == user_id)
            )
            await session.commit()


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
        async with self._session_factory() as session:
            session.add(
                AuditLogRow(
                    id=uuid.uuid4(),
                    actor_user_id=actor_user_id,
                    action_code=action_code,
                    entity_schema=entity_schema,
                    entity_table=entity_table,
                    entity_id=entity_id,
                    old_values=old_values,
                    new_values=new_values,
                    correlation_id=correlation_id,
                    source=source,
                )
            )
            await session.commit()
