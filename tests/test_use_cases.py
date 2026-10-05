"""End-to-end use case tests driving the ``Facade`` with in-memory fakes.

Exercises the real domain guards/errors (not mocks): registering a user,
subscribing/unsubscribing, favorites add/remove and the subscription-limit
``OverflowError``. No network, no database.
"""

from __future__ import annotations

import datetime
import uuid

import pytest
from app.application.facade import Facade
from app.domain.entities import Favorite, Message, Notification, Subscription, User
from app.domain.value_objects import (
    Car,
    Route,
    Station,
    SubscriptionDetails,
    Train,
)


def make_train() -> Train:
    return Train(
        train_type="p",
        train_number="123",
        main_station_from=Station("Минск", "МСК"),
        main_station_to=Station("Гомель", "ГМ"),
        station_from=Station("Минск", "МСК"),
        station_to=Station("Гомель", "ГМ"),
        from_time=datetime.time(8, 0),
        to_time=datetime.time(10, 30),
        train_days="",
        train_days_except="",
        duration_minutes=150,
    )


def make_subscription(date: datetime.date = datetime.date(2026, 8, 22)) -> SubscriptionDetails:
    return SubscriptionDetails(train=make_train(), date=date)


class InMemoryUsers:
    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}

    async def register_user(
        self, telegram_user_id: int, telegram_chat_id: int, username: str | None, display_name: str
    ) -> User:
        for u in self.users.values():
            if u.telegram_user_id == telegram_user_id:
                return u
        uid = uuid.uuid4()
        user = User(
            id=uid,
            telegram_user_id=telegram_user_id,
            telegram_chat_id=telegram_chat_id,
            username=username,
            display_name=display_name,
        )
        self.users[uid] = user
        return user

    async def is_user_registered(self, user_id: uuid.UUID) -> bool:
        return user_id in self.users

    async def add_user(self, user: User) -> None:
        self.users[user.id] = user

    async def get_user_min_interval(self, user_id: uuid.UUID) -> int:
        return self.users[user_id].min_subscriptions_interval

    async def is_user_moderator(self, user_id: uuid.UUID) -> bool:
        return self.users[user_id].is_moderator

    async def get_user_max_subscriptions(self, user_id: uuid.UUID) -> int:
        return self.users[user_id].max_subscriptions

    async def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        return self.users.get(user_id)

    async def set_users_min_interval(self, user_id: uuid.UUID, min_interval: int) -> None:
        self.users[user_id].change_interval_limits(min_interval)

    async def set_users_max_subscriptions(self, user_id: uuid.UUID, max_subscriptions: int) -> None:
        self.users[user_id].change_subscriptions_limits(max_subscriptions)

    async def ban_user(self, user_id: uuid.UUID) -> None:
        self.users[user_id].block()

    async def unban_user(self, user_id: uuid.UUID) -> None:
        self.users[user_id].unblock()

    async def promote_user(self, user_id: uuid.UUID) -> None:
        self.users[user_id].promote()

    async def demote_user(self, user_id: uuid.UUID) -> None:
        self.users[user_id].demote()

    async def is_user_banned(self, user_id: uuid.UUID) -> bool:
        return self.users[user_id].is_blocked

    async def update_activity(self, user_id: uuid.UUID) -> None:
        if user_id in self.users:
            self.users[user_id].last_activity = datetime.datetime.now(datetime.UTC)

    async def get_last_users(self, time_span: datetime.timedelta) -> list[User]:
        return list(self.users.values())

    async def get_moderators(self) -> list[User]:
        return [u for u in self.users.values() if u.is_moderator]


class InMemoryTransport:
    async def get_or_create_service_route(self, details: SubscriptionDetails) -> uuid.UUID:
        return uuid.uuid4()

    async def get_train(self, service_route_id: uuid.UUID) -> Train | None:
        pass


class InMemorySubscriptions:
    def __init__(self) -> None:
        self.subscriptions: list[Subscription] = []

    async def get_user_subscriptions(self, user_id: uuid.UUID) -> list[Subscription]:
        return [s for s in self.subscriptions if s.user_id == user_id]

    async def get_all_subscriptions(self) -> list[Subscription]:
        return list(self.subscriptions)

    async def get_by_id(self, subscription_id: uuid.UUID) -> Subscription | None:
        return next((s for s in self.subscriptions if s.id == subscription_id), None)

    async def add_subscription(self, subscription: Subscription) -> None:
        self.subscriptions.append(subscription)

    async def remove_subscription(self, subscription: Subscription) -> None:
        self.subscriptions.remove(subscription)

    async def subscription_exists(
        self, user_id: uuid.UUID, service_route_id: uuid.UUID, target_date: datetime.date
    ) -> bool:
        return any(
            s.user_id == user_id and s.target_date == target_date
            for s in await self.get_user_subscriptions(user_id)
        )

    async def get_subscription_count(self, user_id: uuid.UUID) -> int:
        return len(await self.get_user_subscriptions(user_id))

    async def claim_due_subscriptions(self, limit: int = 10) -> list[Subscription]:
        return []

    async def save_availability_snapshot(self, subscription_id: uuid.UUID, cars: list[Car]) -> bool:
        return True

    async def update_subscription(self, subscription: Subscription) -> None:
        pass

    async def reset_subscription(self, subscription: Subscription) -> None:
        pass


class InMemoryFavorites:
    def __init__(self) -> None:
        self.favorites: list[Favorite] = []

    async def get_favorites(self, user_id: uuid.UUID) -> list[Favorite]:
        return [f for f in self.favorites if f.user_id == user_id]

    async def add_favorite(self, favorite: Favorite) -> None:
        self.favorites.append(favorite)

    async def remove_favorite(self, favorite: Favorite) -> None:
        for stored in list(self.favorites):
            if stored.id == favorite.id:
                self.favorites.remove(stored)
                return

    async def favorite_exists(self, user_id: uuid.UUID, service_route_id: uuid.UUID) -> bool:
        return any(f.user_id == user_id for f in await self.get_favorites(user_id))


class InMemoryNotifications:
    def __init__(self) -> None:
        self.notifications: list[Notification] = []

    async def claim_pending_notifications(self, limit: int = 50) -> list[Notification]:
        result = self.notifications
        self.notifications = []
        return result

    async def mark_sent(self, notification_id: uuid.UUID) -> None:
        pass

    async def mark_failed(self, notification_id: uuid.UUID, error_text: str) -> None:
        pass

    async def add_notification(self, notification: Notification) -> None:
        self.notifications.append(notification)


class NoopMessages:
    async def add_message(self, message: Message) -> None: ...
    async def get_user_messages(self, user_id: uuid.UUID) -> list:
        return []

    async def get_all_messages(self) -> list:
        return []


class NoopRw:
    async def get_stations(self, prefix: str) -> list[Station]:
        return []

    async def get_trains(self, route: Route) -> list[Train]:
        return []

    async def get_seats(self, details: SubscriptionDetails) -> list[Car]:
        return []


@pytest.fixture
def facade() -> tuple[Facade, InMemoryUsers, InMemorySubscriptions, InMemoryFavorites]:
    users = InMemoryUsers()
    transport = InMemoryTransport()
    subscriptions = InMemorySubscriptions()
    favorites = InMemoryFavorites()
    notifications = InMemoryNotifications()
    fac = Facade(
        users=users,
        transport=transport,
        subscriptions=subscriptions,
        favorites=favorites,
        notifications=notifications,
        messages=NoopMessages(),
        rw=NoopRw(),
    )
    return fac, users, subscriptions, favorites


async def test_subscribe_get_and_unsubscribe_flow(
    facade: tuple[Facade, InMemoryUsers, InMemorySubscriptions, InMemoryFavorites],
) -> None:
    fac, _users, subscriptions, _favorites = facade
    user_id = await fac.register_user(1, 1, "testuser1", "Test User 1")
    details = make_subscription()

    await fac.subscribe(user_id, details)
    assert await fac.get_subscriptions(user_id, user_id) == [details]

    await fac.unsubscribe(user_id, details)
    assert await fac.get_subscriptions(user_id, user_id) == []
    assert await subscriptions.get_user_subscriptions(user_id) == []

    with pytest.raises(RuntimeError):
        await fac.unsubscribe(user_id, details)


async def test_subscription_limit_exceeded_raises_overflow(
    facade: tuple[Facade, InMemoryUsers, InMemorySubscriptions, InMemoryFavorites],
) -> None:
    fac, users, _subscriptions, _favorites = facade
    uid = await fac.register_user(2, 2, "testuser2", "Test User 2")
    users.users[uid].change_subscriptions_limits(1)

    await fac.subscribe(uid, make_subscription(datetime.date(2026, 8, 22)))
    with pytest.raises(OverflowError):
        await fac.subscribe(uid, make_subscription(datetime.date(2026, 8, 23)))


async def test_favorites_add_and_remove_flow(
    facade: tuple[Facade, InMemoryUsers, InMemorySubscriptions, InMemoryFavorites],
) -> None:
    fac, _users, _subscriptions, _favorites = facade
    uid = await fac.register_user(3, 3, "testuser", "Test User")
    train = make_train()

    assert await fac.is_in_favorites(uid, train) is False
    await fac.add_to_favorites(uid, train)
    assert await fac.is_in_favorites(uid, train) is True
    assert await fac.get_favorites(uid) == [train]

    await fac.remove_from_favorites(uid, train)
    assert await fac.is_in_favorites(uid, train) is False

    with pytest.raises(KeyError):
        await fac.remove_from_favorites(uid, train)


async def test_unknown_user_is_rejected(
    facade: tuple[Facade, InMemoryUsers, InMemorySubscriptions, InMemoryFavorites],
) -> None:
    fac, _users, _subscriptions, _favorites = facade
    ghost_uuid = uuid.uuid4()
    with pytest.raises(KeyError):
        await fac.subscribe(ghost_uuid, make_subscription())
