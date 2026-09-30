"""PostgreSQL repositories implementing the normalized schema using SQLAlchemy ORM."""

from __future__ import annotations

import contextlib
import datetime
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import delete, func, select, update

from app.domain.entities import Favorite, Message, Notification, Subscription, User
from app.domain.value_objects import Car, CarType, Station, SubscriptionDetails, Train
from app.infrastructure.db.models import (
    AvailabilitySnapshotRow,
    AvailabilitySnapshotSeatRow,
    FavoriteRow,
    MessageRow,
    NotificationRow,
    ProviderRow,
    RoleRow,
    ServiceRouteRow,
    ServiceRow,
    StopRow,
    SubscriptionRow,
    UserRoleRow,
    UserRow,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from app.domain.protocols import Logger

UTC = datetime.UTC


class _RepositoryBase:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------


def user_row_to_entity(row: UserRow) -> User:
    return User(
        id=row.id,
        telegram_user_id=row.telegram_user_id,
        telegram_chat_id=row.telegram_chat_id,
        username=row.username,
        display_name=row.display_name,
        is_moderator=row.status == "ACTIVE",
        max_subscriptions=row.max_subscriptions,
        min_subscriptions_interval=row.min_subscription_interval_seconds,
        status=row.status,
        last_activity=row.last_activity_at,
    )


# ---------------------------------------------------------------------------
# UserRepository
# ---------------------------------------------------------------------------


class UserPostgresRepository(_RepositoryBase):
    async def register_user(
        self, telegram_user_id: int, telegram_chat_id: int, username: str | None, display_name: str
    ) -> User:
        async with self._session_factory() as session:
            role_count = await session.scalar(select(func.count()).select_from(RoleRow))
            if not role_count or role_count == 0:
                session.add(RoleRow(id=1, code="USER", name="User"))
                session.add(RoleRow(id=2, code="MODERATOR", name="Moderator"))
                session.add(RoleRow(id=3, code="ADMIN", name="Administrator"))
                await session.flush()

            stmt = select(UserRow).where(UserRow.telegram_user_id == telegram_user_id)
            row = await session.scalar(stmt)
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
                    last_activity_at=datetime.datetime.now(UTC),
                )
                session.add(row)
                await session.flush()
            else:
                row.telegram_chat_id = telegram_chat_id
                row.last_activity_at = datetime.datetime.now(UTC)
                await session.flush()

            # TODO: not moderator role for new users
            mod_role = await session.scalar(select(RoleRow).where(RoleRow.code == "MODERATOR"))
            if mod_role:
                existing_ur = await session.scalar(
                    select(UserRoleRow).where(
                        UserRoleRow.user_id == row.id, UserRoleRow.role_id == mod_role.id
                    )
                )
                if not existing_ur:
                    session.add(UserRoleRow(user_id=row.id, role_id=mod_role.id))

            await session.commit()
            await session.refresh(row)
            return user_row_to_entity(row)

    async def is_user_registered(self, user_id: uuid.UUID) -> bool:
        async with self._session_factory() as session:
            result = await session.scalars(select(UserRow.id).where(UserRow.id == user_id).limit(1))
            return result.first() is not None

    async def add_user(self, user: User) -> None:
        async with self._session_factory() as session:
            row = UserRow(
                id=user.id,
                telegram_user_id=user.telegram_user_id,
                telegram_chat_id=user.telegram_chat_id,
                status=user.status,
                max_subscriptions=user.max_subscriptions,
                min_subscription_interval_seconds=user.min_subscriptions_interval,
                last_activity_at=user.last_activity,
            )
            session.add(row)
            await session.commit()

    async def get_user_min_interval(self, user_id: uuid.UUID) -> int:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            return row.min_subscription_interval_seconds

    async def is_user_moderator(self, user_id: uuid.UUID) -> bool:
        async with self._session_factory() as session:
            row = await session.scalar(select(UserRow).where(UserRow.id == user_id))
            return row is None or row.status != "BLOCKED"

    async def get_user_max_subscriptions(self, user_id: uuid.UUID) -> int:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            return row.max_subscriptions

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        async with self._session_factory() as session:
            row = await session.scalar(select(UserRow).where(UserRow.id == user_id))
            return user_row_to_entity(row) if row else None

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
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.status = "ACTIVE"
            mod_role = await session.scalar(select(RoleRow).where(RoleRow.code == "MODERATOR"))
            if mod_role:
                existing_ur = await session.scalar(
                    select(UserRoleRow).where(
                        UserRoleRow.user_id == user_id, UserRoleRow.role_id == mod_role.id
                    )
                )
                if not existing_ur:
                    session.add(UserRoleRow(user_id=user_id, role_id=mod_role.id))
            await session.commit()

    async def demote_user(self, user_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            mod_role = await session.scalar(select(RoleRow).where(RoleRow.code == "MODERATOR"))
            if mod_role:
                await session.execute(
                    delete(UserRoleRow).where(
                        UserRoleRow.user_id == user_id, UserRoleRow.role_id == mod_role.id
                    )
                )
            await session.commit()

    async def is_user_banned(self, user_id: uuid.UUID) -> bool:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            return row.status == "BLOCKED"

    async def update_activity(self, user_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            row = await session.scalar(select(UserRow).where(UserRow.id == user_id))
            if row:
                row.last_activity_at = datetime.datetime.now(UTC)
                await session.commit()

    async def get_last_users(self, time_span: datetime.timedelta) -> list[User]:
        cutoff = datetime.datetime.now(UTC) - time_span
        async with self._session_factory() as session:
            rows = await session.scalars(select(UserRow).where(UserRow.last_activity_at >= cutoff))
            return [user_row_to_entity(r) for r in rows]

    async def get_moderators(self) -> list[User]:
        async with self._session_factory() as session:
            rows = await session.scalars(select(UserRow).where(UserRow.status == "ACTIVE"))
            return [user_row_to_entity(r) for r in rows]

    async def _user_or_raise(self, session: AsyncSession, user_id: uuid.UUID) -> UserRow:
        row = await session.scalar(select(UserRow).where(UserRow.id == user_id))
        if row is None:
            raise KeyError(f"User {user_id} not found")
        return row


# ---------------------------------------------------------------------------
# TransportRepository
# ---------------------------------------------------------------------------


class TransportPostgresRepository(_RepositoryBase):
    async def get_or_create_service_route(self, details: SubscriptionDetails) -> uuid.UUID:
        train = details.train
        async with self._session_factory() as session:
            provider = await session.scalar(select(ProviderRow).where(ProviderRow.code == "RW_BY"))
            if not provider:
                provider = ProviderRow(
                    id=uuid.uuid4(),
                    code="RW_BY",
                    name="Белорусская железная дорога",
                    adapter_code="rw_by",
                    is_active=True,
                )
                session.add(provider)
                await session.flush()

            from_stop = await session.scalar(
                select(StopRow).where(
                    StopRow.provider_id == provider.id,
                    StopRow.external_code == train.station_from.label,
                )
            )
            if not from_stop:
                from_stop = StopRow(
                    id=uuid.uuid4(),
                    provider_id=provider.id,
                    external_code=train.station_from.label,
                    name=train.title_station_from,
                )
                session.add(from_stop)
                await session.flush()

            to_stop = await session.scalar(
                select(StopRow).where(
                    StopRow.provider_id == provider.id,
                    StopRow.external_code == train.station_to.label,
                )
            )
            if not to_stop:
                to_stop = StopRow(
                    id=uuid.uuid4(),
                    provider_id=provider.id,
                    external_code=train.station_to.label,
                    name=train.title_station_to,
                )
                session.add(to_stop)
                await session.flush()

            service = await session.scalar(
                select(ServiceRow).where(
                    ServiceRow.provider_id == provider.id,
                    ServiceRow.transport_mode == "TRAIN",
                    ServiceRow.external_number == train.train_number,
                )
            )
            if not service:
                service = ServiceRow(
                    id=uuid.uuid4(),
                    provider_id=provider.id,
                    transport_mode="TRAIN",
                    external_number=train.train_number,
                    service_type=train.train_type,
                    display_name=train.train_number,
                )
                session.add(service)
                await session.flush()

            route = await session.scalar(
                select(ServiceRouteRow).where(
                    ServiceRouteRow.service_id == service.id,
                    ServiceRouteRow.from_stop_id == from_stop.id,
                    ServiceRouteRow.to_stop_id == to_stop.id,
                )
            )
            if not route:
                route = ServiceRouteRow(
                    id=uuid.uuid4(),
                    service_id=service.id,
                    from_stop_id=from_stop.id,
                    to_stop_id=to_stop.id,
                    departure_time=train.from_time,
                    arrival_time=train.to_time,
                    duration_minutes=train.duration_minutes,
                    days_rule=train.train_days,
                    days_exceptions=train.train_days_except,
                )
                session.add(route)
                await session.commit()
            else:
                route.departure_time = train.from_time
                route.arrival_time = train.to_time
                route.duration_minutes = train.duration_minutes
                route.days_rule = train.train_days
                route.days_exceptions = train.train_days_except
                await session.commit()

            return route.id


# ---------------------------------------------------------------------------
# SubscriptionRepository
# ---------------------------------------------------------------------------


class SubscriptionPostgresRepository(_RepositoryBase):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        transport_repo: TransportPostgresRepository,
        logger: Logger,
    ) -> None:
        super().__init__(session_factory)
        self._transport_repo = transport_repo
        self._logger = logger

    async def get_user_subscriptions(self, user_id: uuid.UUID) -> list[Subscription]:
        async with self._session_factory() as session:
            rows = await session.scalars(
                select(SubscriptionRow).where(
                    SubscriptionRow.user_id == user_id,
                    SubscriptionRow.status.in_(["ACTIVE", "PAUSED"]),
                )
            )
            return [await self._row_to_subscription(session, r) for r in rows]

    async def get_all_subscriptions(self) -> list[Subscription]:
        async with self._session_factory() as session:
            rows = await session.scalars(
                select(SubscriptionRow).where(SubscriptionRow.status.in_(["ACTIVE", "PAUSED"]))
            )
            return [await self._row_to_subscription(session, r) for r in rows]

    async def get_by_id(self, subscription_id: uuid.UUID) -> Subscription | None:
        async with self._session_factory() as session:
            row = await session.scalar(
                select(SubscriptionRow).where(SubscriptionRow.id == subscription_id)
            )
            if not row:
                return None
            return await self._row_to_subscription(session, row)

    async def add_subscription(self, subscription: Subscription) -> None:
        service_route_id = await self._transport_repo.get_or_create_service_route(
            subscription.details
        )
        async with self._session_factory() as session:
            row = SubscriptionRow(
                id=subscription.id,
                user_id=subscription.user_id,
                service_route_id=service_route_id,
                target_date=subscription.details.date,
                status=subscription.status,
                next_check_at=datetime.datetime.now(UTC),
            )
            session.add(row)
            await session.commit()

    async def remove_subscription(self, subscription: Subscription) -> None:
        async with self._session_factory() as session:
            row = await session.get(SubscriptionRow, subscription.id)
            if row:
                row.status = "CANCELLED"
                await session.commit()

    async def subscription_exists(
        self, user_id: uuid.UUID, service_route_id: uuid.UUID, target_date: datetime.date
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
            if row:
                row.last_checked_at = subscription.last_checked_at
                row.next_check_at = subscription.next_check_at
                await session.commit()

    async def reset_subscription(self, subscription: Subscription) -> None:
        async with self._session_factory() as session:
            row = await session.get(SubscriptionRow, subscription.id)
            if row:
                row.next_check_at = datetime.datetime.now(UTC)
                await session.commit()

    async def claim_due_subscriptions(self, limit: int = 10) -> list[Subscription]:
        async with self._session_factory() as session:
            subquery = (
                select(SubscriptionRow.id)
                .where(
                    SubscriptionRow.status == "ACTIVE",
                    SubscriptionRow.next_check_at.is_(None)
                    | (SubscriptionRow.next_check_at <= datetime.datetime.now(UTC)),
                )
                .order_by(SubscriptionRow.next_check_at, SubscriptionRow.id)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )
            sub_ids = (await session.scalars(subquery)).all()
            if not sub_ids:
                await session.commit()
                return []

            await session.execute(
                update(SubscriptionRow)
                .where(SubscriptionRow.id.in_(sub_ids))
                .values(next_check_at=datetime.datetime.now(UTC) + datetime.timedelta(minutes=5))
            )
            await session.commit()

        async with self._session_factory() as session:
            rows = await session.scalars(
                select(SubscriptionRow).where(SubscriptionRow.id.in_(sub_ids))
            )
            return [await self._row_to_subscription(session, r) for r in rows]

    async def save_availability_snapshot(self, subscription_id: uuid.UUID, cars: list[Car]) -> bool:
        async with self._session_factory() as session:
            snapshot_id = uuid.uuid4()
            now = datetime.datetime.now(UTC)
            session.add(
                AvailabilitySnapshotRow(
                    id=snapshot_id,
                    subscription_id=subscription_id,
                    checked_at=now,
                )
            )
            for car in cars:
                for seat in car.free_seats:
                    session.add(
                        AvailabilitySnapshotSeatRow(
                            snapshot_id=snapshot_id,
                            unit_type=car.car_type,
                            unit_number=car.number,
                            place_code=str(seat),
                        )
                    )
            await session.commit()
        return True

    async def _row_to_subscription(
        self, session: AsyncSession, row: SubscriptionRow
    ) -> Subscription:
        sr = await session.get(ServiceRouteRow, row.service_route_id)
        train_info = None
        if sr:
            service = await session.get(ServiceRow, sr.service_id)
            from_stop = await session.get(StopRow, sr.from_stop_id)
            to_stop = await session.get(StopRow, sr.to_stop_id)
            if service and from_stop and to_stop:
                train_info = Train(
                    train_type=service.service_type or "p",
                    train_number=service.external_number,
                    title_station_from=from_stop.name,
                    title_station_to=to_stop.name,
                    station_from=Station(from_stop.name, from_stop.external_code),
                    station_to=Station(to_stop.name, to_stop.external_code),
                    from_time=sr.departure_time,
                    to_time=sr.arrival_time,
                    train_days=sr.days_rule or "",
                    train_days_except=sr.days_exceptions or "",
                    duration_minutes=sr.duration_minutes,
                )
        details = SubscriptionDetails(
            train=train_info
            or Train(
                "p",
                "0",
                "",
                "",
                Station("", ""),
                Station("", ""),
                datetime.time(0, 0),
                datetime.time(0, 0),
                "",
                "",
                0,
            ),
            date=row.target_date,
        )

        latest_snap = await session.scalar(
            select(AvailabilitySnapshotRow)
            .where(AvailabilitySnapshotRow.subscription_id == row.id)
            .order_by(AvailabilitySnapshotRow.checked_at.desc())
            .limit(1)
        )
        last_state = []
        if latest_snap:
            seat_rows = (
                await session.scalars(
                    select(AvailabilitySnapshotSeatRow).where(
                        AvailabilitySnapshotSeatRow.snapshot_id == latest_snap.id
                    )
                )
            ).all()
            cars_map: dict[tuple[str, str], list[int]] = {}
            for sr_seat in seat_rows:
                key = (sr_seat.unit_type, sr_seat.unit_number)
                if key not in cars_map:
                    cars_map[key] = []
                with contextlib.suppress(ValueError):
                    cars_map[key].append(int(sr_seat.place_code))
            for (ut, un), seats in cars_map.items():
                last_state.append(
                    Car(
                        car_type=CarType(int(ut)),
                        number=int(un),
                        free_seats=tuple(sorted(seats)),
                    )
                )

        return Subscription(
            id=row.id,
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
# FavoritesRepository
# ---------------------------------------------------------------------------


class FavoritesPostgresRepository(_RepositoryBase):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        transport_repo: TransportPostgresRepository,
        logger: Logger,
    ) -> None:
        super().__init__(session_factory)
        self._transport_repo = transport_repo
        self._logger = logger

    async def get_favorites(self, user_id: uuid.UUID) -> list[Favorite]:
        async with self._session_factory() as session:
            rows = await session.scalars(select(FavoriteRow).where(FavoriteRow.user_id == user_id))
            favorites = []
            for row in rows:
                sr = await session.get(ServiceRouteRow, row.service_route_id)
                if not sr:
                    raise ValueError("Invalid service_route data")
                service = await session.get(ServiceRow, sr.service_id)
                from_stop = await session.get(StopRow, sr.from_stop_id)
                to_stop = await session.get(StopRow, sr.to_stop_id)
                if not (service and from_stop and to_stop):
                    raise ValueError("Invalid favorite data")
                train_info = Train(
                    train_type=service.service_type or "p",
                    train_number=service.external_number,
                    title_station_from=from_stop.name,
                    title_station_to=to_stop.name,
                    station_from=Station(from_stop.name, from_stop.external_code),
                    station_to=Station(to_stop.name, to_stop.external_code),
                    from_time=sr.departure_time,
                    to_time=sr.arrival_time,
                    train_days=sr.days_rule or "",
                    train_days_except=sr.days_exceptions or "",
                    duration_minutes=sr.duration_minutes,
                )
                favorites.append(
                    Favorite(
                        id=row.id,
                        user_id=row.user_id,
                        service_route_id=row.service_route_id,
                        train_info=train_info,
                    )
                )
            return favorites

    async def add_favorite(self, favorite: Favorite) -> None:
        service_route_id = await self._transport_repo.get_or_create_service_route(
            SubscriptionDetails(train=favorite.train_info, date=datetime.date.today())
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
# NotificationRepository (Transactional Outbox)
# ---------------------------------------------------------------------------


class NotificationPostgresRepository(_RepositoryBase):
    async def claim_pending_notifications(self, limit: int = 50) -> list[Notification]:
        async with self._session_factory() as session:
            stuck_cutoff = datetime.datetime.now(UTC) - datetime.timedelta(minutes=5)
            await session.execute(
                update(NotificationRow)
                .where(
                    NotificationRow.status == "PROCESSING",
                    NotificationRow.locked_at <= stuck_cutoff,
                )
                .values(status="PENDING", locked_at=None)
            )
            await session.commit()

            claimed_ids = (
                await session.scalars(
                    select(NotificationRow.id)
                    .where(
                        NotificationRow.status == "PENDING",
                        NotificationRow.available_at <= datetime.datetime.now(UTC),
                        NotificationRow.attempts < 5,
                    )
                    .order_by(NotificationRow.available_at, NotificationRow.id)
                    .limit(limit)
                    .with_for_update(skip_locked=True)
                )
            ).all()
            if not claimed_ids:
                await session.commit()
                return []

            await session.execute(
                update(NotificationRow)
                .where(NotificationRow.id.in_(claimed_ids))
                .values(
                    status="PROCESSING",
                    locked_at=datetime.datetime.now(UTC),
                    attempts=NotificationRow.attempts + 1,
                )
            )
            await session.commit()

        async with self._session_factory() as session:
            rows = await session.scalars(
                select(NotificationRow).where(NotificationRow.id.in_(claimed_ids))
            )
            return [
                Notification(
                    id=r.id,
                    user_id=r.user_id,
                    content=r.content,
                    subscription_id=r.subscription_id,
                    notification_type=r.notification_type,
                    status=r.status,
                    attempts=r.attempts,
                )
                for r in rows
            ]

    async def mark_sent(self, notification_id: uuid.UUID) -> None:
        async with self._session_factory() as session:
            row = await session.get(NotificationRow, notification_id)
            if row:
                row.status = "SENT"
                row.sent_at = datetime.datetime.now(UTC)
                await session.commit()

    async def mark_failed(self, notification_id: uuid.UUID, error_text: str) -> None:
        async with self._session_factory() as session:
            row = await session.get(NotificationRow, notification_id)
            if row:
                row.status = "PENDING"
                row.available_at = datetime.datetime.now(UTC) + datetime.timedelta(
                    seconds=10 * (2**row.attempts)
                )
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
                    available_at=notification.available_at or datetime.datetime.now(UTC),
                )
            )
            await session.commit()


# ---------------------------------------------------------------------------
# MessageRepository
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
                    sent_at=message.sent_date,
                )
            )
            await session.commit()

    async def get_user_messages(self, user_id: uuid.UUID) -> list[Message]:
        async with self._session_factory() as session:
            rows = await session.scalars(
                select(MessageRow)
                .where(
                    (MessageRow.receiver_user_id == user_id)
                    | (MessageRow.sender_user_id == user_id)
                )
                .order_by(MessageRow.sent_at)
            )
            return [
                Message(
                    id=r.id,
                    sender_id=r.sender_user_id,
                    receiver_id=r.receiver_user_id,
                    content=r.content,
                    sent_date=r.sent_at,
                )
                for r in rows
            ]

    async def get_all_messages(self) -> list[Message]:
        async with self._session_factory() as session:
            rows = await session.scalars(select(MessageRow))
            return [
                Message(
                    id=r.id,
                    sender_id=r.sender_user_id,
                    receiver_id=r.receiver_user_id,
                    content=r.content,
                    sent_date=r.sent_at,
                )
                for r in rows
            ]
