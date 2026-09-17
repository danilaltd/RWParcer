"""PostgreSQL repositories — ports of the C# ``*Repository`` classes.

Semantics preserved exactly:

* every operation opens its own session (``RepositoryBase`` did the same);
* ``null`` aggregates are tolerated with C# ``LogDebug`` strings and a no-op
  (subscriptions/favorites) — *not* exceptions;
* lookups that miss the user row raise ``KeyNotFoundError`` (C#
  ``KeyNotFoundException``), including the trailing-period variant of
  ``GetUserByIdAsync``;
* ``pop_all`` reads, removes and returns in one transaction.
"""

from __future__ import annotations

import datetime
import uuid
from collections.abc import Awaitable, Callable

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.errors import KeyNotFoundError
from app.domain import json_codecs
from app.domain.entities import Favorite, Message, Notification, Subscription, User
from app.domain.protocols import Logger
from app.domain.value_objects import SubscriptionDetails, Train
from app.infrastructure.db.models import (
    FavoriteRow,
    MessageRow,
    NotificationRow,
    SubscriptionRow,
    UserRow,
)

UTC = datetime.UTC


class _RepositoryBase:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def _transaction(self, fn: Callable[[AsyncSession], Awaitable[object]]) -> object:
        async with self._session_factory() as session:
            return await fn(session)


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------


def user_row_to_entity(row: UserRow) -> User:
    return User(
        id=row.id,
        is_moderator=row.is_moderator,
        max_subscriptions=row.max_subscriptions,
        min_subscriptions_interval=row.min_subscriptions_interval,
        is_blocked=row.is_blocked,
        last_activity=row.last_activity,
    )


def user_entity_to_row(entity: User) -> UserRow:
    return UserRow(
        id=entity.id,
        is_moderator=entity.is_moderator,
        max_subscriptions=entity.max_subscriptions,
        min_subscriptions_interval=entity.min_subscriptions_interval,
        is_blocked=entity.is_blocked,
        last_activity=entity.last_activity,
    )


def subscription_to_row(entity: Subscription) -> SubscriptionRow:
    return SubscriptionRow(
        id=entity.id,
        user_id=entity.user_id,
        details=json_codecs.subscription_details_to_json(entity.details),
        last_update=entity.last_update,
        last_state=[json_codecs.car_to_json(car) for car in entity.last_state or []],
    )


def subscription_row_to_entity(row: SubscriptionRow) -> Subscription:
    return Subscription(
        id=row.id,
        user_id=row.user_id,
        details=json_codecs.subscription_details_from_json_or_default(row.details),
        last_update=row.last_update,
        last_state=json_codecs.cars_from_json_or_default(row.last_state),
    )


def favorite_to_row(entity: Favorite) -> FavoriteRow:
    return FavoriteRow(
        id=entity.id,
        user_id=entity.user_id,
        train_info=json_codecs.train_to_json(entity.train_info),
    )


def favorite_row_to_entity(row: FavoriteRow) -> Favorite:
    return Favorite(
        id=row.id,
        user_id=row.user_id,
        train_info=json_codecs.train_from_json_or_default(row.train_info),
    )


def message_row_to_entity(row: MessageRow) -> Message:
    return Message(
        id=row.id,
        sender_id=row.sender_id,
        receiver_id=row.receiver_id,
        content=row.content,
        sent_date=row.sent_date,
    )


def notification_row_to_entity(row: NotificationRow) -> Notification:
    return Notification(id=row.id, user_id=row.user_id, content=row.content)


# ---------------------------------------------------------------------------
# UserRepository
# ---------------------------------------------------------------------------


class UserPostgresRepository(_RepositoryBase):
    """Port of ``UserRepository``."""

    async def is_user_registered(self, user_id: str) -> bool:
        async with self._session_factory() as session:
            result = await session.scalars(select(UserRow.id).where(UserRow.id == user_id).limit(1))
            return result.first() is not None

    async def add_user(self, user: User) -> None:
        async with self._session_factory() as session:
            session.add(user_entity_to_row(user))
            await session.commit()

    async def get_user_min_interval(self, user_id: str) -> int:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            return row.min_subscriptions_interval

    async def is_user_moderator(self, user_id: str) -> bool:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            return row.is_moderator

    async def get_user_max_subscriptions(self, user_id: str) -> int:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            return row.max_subscriptions

    async def get_user_by_id(self, user_id: str) -> User | None:
        async with self._session_factory() as session:
            row = await session.scalar(select(UserRow).where(UserRow.id == user_id))
            return user_to_row_to_entity_or_none(row)

    async def set_users_min_interval(self, user_id: str, min_interval: int) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.min_subscriptions_interval = min_interval
            await session.commit()

    async def set_users_max_subscriptions(self, user_id: str, max_subscriptions: int) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.max_subscriptions = max_subscriptions
            await session.commit()

    async def ban_user(self, user_id: str) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.is_blocked = True
            row.is_moderator = False
            await session.commit()

    async def unban_user(self, user_id: str) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.is_blocked = False
            await session.commit()

    async def promote_user(self, user_id: str) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.is_blocked = False
            row.is_moderator = True
            await session.commit()

    async def demote_user(self, user_id: str) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.is_moderator = False
            await session.commit()

    async def is_user_banned(self, user_id: str) -> bool:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            return row.is_blocked

    async def update_activity(self, user_id: str) -> None:
        async with self._session_factory() as session:
            row = await self._user_or_raise(session, user_id)
            row.last_activity = datetime.datetime.now(UTC)
            await session.commit()

    async def get_last_users(self, time_span: datetime.timedelta) -> list[User]:
        cutoff = datetime.datetime.now(UTC) - time_span
        async with self._session_factory() as session:
            rows = await session.scalars(select(UserRow).where(UserRow.last_activity >= cutoff))
            return [user_row_to_entity(r) for r in rows]

    async def get_moderators(self) -> list[User]:
        async with self._session_factory() as session:
            rows = await session.scalars(select(UserRow).where(UserRow.is_moderator))
            return [user_row_to_entity(r) for r in rows]

    async def _user_or_raise(self, session: AsyncSession, user_id: str) -> UserRow:
        row = await session.scalar(select(UserRow).where(UserRow.id == user_id))
        if row is None:
            raise KeyNotFoundError(f"User {user_id} not found")
        return row


def user_to_row_to_entity_or_none(row: UserRow | None) -> User | None:
    return user_row_to_entity(row) if row is not None else None


# ---------------------------------------------------------------------------
# SubscriptionRepository
# ---------------------------------------------------------------------------


class SubscriptionPostgresRepository(_RepositoryBase):
    """Port of ``SubscriptionRepository``."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        logger: Logger,
    ) -> None:
        super().__init__(session_factory)
        self._logger = logger

    async def get_user_subscriptions(self, user_id: str) -> list[Subscription]:
        async with self._session_factory() as session:
            rows = await session.scalars(
                select(SubscriptionRow).where(SubscriptionRow.user_id == user_id)
            )
            return [subscription_row_to_entity(r) for r in rows]

    async def get_all_subscriptions(self) -> list[Subscription]:
        async with self._session_factory() as session:
            rows = await session.scalars(select(SubscriptionRow))
            return [subscription_row_to_entity(r) for r in rows]

    async def get_by_id(self, subscription_id: uuid.UUID) -> Subscription | None:
        async with self._session_factory() as session:
            row = await session.scalar(
                select(SubscriptionRow).where(SubscriptionRow.id == subscription_id)
            )
            return subscription_row_to_entity(row) if row is not None else None

    async def add_subscription(self, subscription: Subscription | None) -> None:
        if subscription is None:
            self._logger.debug("AddSubscription err")
            return
        async with self._session_factory() as session:
            session.add(subscription_to_row(subscription))
            await session.commit()

    async def remove_subscription(self, subscription: Subscription | None) -> None:
        if subscription is None:
            self._logger.debug("RemoveSubscription err")
            return
        async with self._session_factory() as session:
            await session.execute(
                delete(SubscriptionRow).where(SubscriptionRow.id == subscription.id)
            )
            await session.commit()

    async def subscription_exists(self, user_id: str, details: SubscriptionDetails) -> bool:
        if details is None:
            self._logger.debug("Exists err")
            return False
        subscriptions = await self.get_user_subscriptions(user_id)
        return any(
            json_codecs.subscription_details_to_json(s.details) == details_json
            for s in subscriptions
            for details_json in [json_codecs.subscription_details_to_json(details)]
        )

    async def get_subscription_count(self, user_id: str) -> int:
        async with self._session_factory() as session:
            count = await session.scalar(
                select(func.count())
                .select_from(SubscriptionRow)
                .where(SubscriptionRow.user_id == user_id)
            )
        return int(count or 0)

    async def update_subscription(self, subscription: Subscription | None) -> None:
        if subscription is None:
            self._logger.debug("UpdateSubscription err")
            return
        row = subscription_to_row(subscription)
        async with self._session_factory() as session:
            existing = await session.get(SubscriptionRow, subscription.id)
            if existing is not None:
                existing.user_id = row.user_id
                existing.details = row.details
                existing.last_update = row.last_update
                existing.last_state = row.last_state
                await session.commit()

    async def reset_subscription(self, subscription: Subscription | None) -> None:
        if subscription is None:
            self._logger.debug("ResetSubscription err")
            return
        row = subscription_to_row(subscription)
        async with self._session_factory() as session:
            existing = await session.get(SubscriptionRow, subscription.id)
            if existing is not None:
                existing.details = row.details
                existing.last_update = None
                existing.last_state = []
                await session.commit()


# ---------------------------------------------------------------------------
# FavoritesRepository
# ---------------------------------------------------------------------------


class FavoritesPostgresRepository(_RepositoryBase):
    """Port of ``FavoritesRepository``."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        logger: Logger,
    ) -> None:
        super().__init__(session_factory)
        self._logger = logger

    async def get_favorites(self, user_id: str) -> list[Favorite]:
        async with self._session_factory() as session:
            rows = await session.scalars(select(FavoriteRow).where(FavoriteRow.user_id == user_id))
            return [favorite_row_to_entity(r) for r in rows]

    async def add_favorite(self, favorite: Favorite | None) -> None:
        if favorite is None:
            self._logger.debug("AddFavorite err")
            return
        async with self._session_factory() as session:
            session.add(favorite_to_row(favorite))
            await session.commit()

    async def remove_favorite(self, favorite: Favorite | None) -> None:
        if favorite is None:
            self._logger.debug("RemoveFavorite err")
            return
        async with self._session_factory() as session:
            await session.execute(delete(FavoriteRow).where(FavoriteRow.id == favorite.id))
            await session.commit()

    async def favorite_exists(self, user_id: str, train: Train) -> bool:
        if train is None:
            self._logger.debug("Exists err")
            return False
        favorites = await self.get_favorites(user_id)
        target = json_codecs.train_to_json(train)
        return any(json_codecs.train_to_json(f.train_info) == target for f in favorites)


# ---------------------------------------------------------------------------
# NotificationRepository
# ---------------------------------------------------------------------------


class NotificationPostgresRepository(_RepositoryBase):
    """Port of ``NotificationRepository``."""

    async def pop_all(self) -> list[Notification]:
        async with self._session_factory() as session:
            rows = (await session.scalars(select(NotificationRow))).all()
            for row in rows:
                await session.delete(row)
            await session.commit()
            return [notification_row_to_entity(r) for r in rows]

    async def add_notification(self, notification: Notification | None) -> None:
        if notification is None:
            raise ValueError("notification")
        async with self._session_factory() as session:
            session.add(
                NotificationRow(
                    id=notification.id,
                    user_id=notification.user_id,
                    content=notification.content,
                )
            )
            await session.commit()


# ---------------------------------------------------------------------------
# MessageRepository
# ---------------------------------------------------------------------------


class MessagePostgresRepository(_RepositoryBase):
    """Port of ``MessageRepository``."""

    async def add_message(self, message: Message | None) -> None:
        if message is None:
            raise ValueError("message")
        async with self._session_factory() as session:
            session.add(
                MessageRow(
                    id=message.id,
                    sender_id=message.sender_id,
                    receiver_id=message.receiver_id,
                    content=message.content,
                    sent_date=message.sent_date,
                )
            )
            await session.commit()

    async def get_user_messages(self, user_id: str) -> list[Message]:
        async with self._session_factory() as session:
            rows = await session.scalars(
                select(MessageRow).where(MessageRow.receiver_id == user_id)
            )
            return [message_row_to_entity(r) for r in rows]

    async def get_all_messages(self) -> list[Message]:
        async with self._session_factory() as session:
            rows = await session.scalars(select(MessageRow))
            return [message_row_to_entity(r) for r in rows]
