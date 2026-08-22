"""End-to-end use case tests driving the ``Facade`` with in-memory fakes.

Exercises the real domain guards/errors (not mocks): registering a user,
subscribing/unsubscribing, favorites add/remove and the subscription-limit
``OverflowError``. No network, no database.
"""

from __future__ import annotations

import datetime
import uuid

import pytest
from app.application.errors import InvalidOperationError, KeyNotFoundError
from app.application.facade import Facade
from app.domain.entities import Favorite, Notification, Subscription, User
from app.domain.value_objects import (
    Car,
    Station,
    SubscriptionDetails,
    Train,
)


def make_train() -> Train:
    return Train(
        train_type="p",
        train_number="123",
        title_station_from="Минск",
        title_station_to="Гомель",
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
        self.users: dict[str, User] = {}

    async def is_user_registered(self, user_id: str) -> bool:
        return user_id in self.users

    async def add_user(self, user: User) -> None:
        self.users[user.id] = user

    async def get_user_min_interval(self, user_id: str) -> int:
        return self.users[user_id].min_subscriptions_interval

    async def is_user_moderator(self, user_id: str) -> bool:
        return self.users[user_id].is_moderator

    async def get_user_max_subscriptions(self, user_id: str) -> int:
        return self.users[user_id].max_subscriptions

    async def get_user_by_id(self, user_id: str) -> User | None:
        return self.users.get(user_id)

    async def set_users_min_interval(self, user_id: str, min_interval: int) -> None:
        self.users[user_id].change_interval_limits(min_interval)

    async def set_users_max_subscriptions(self, user_id: str, max_subscriptions: int) -> None:
        self.users[user_id].change_subscriptions_limits(max_subscriptions)

    async def ban_user(self, user_id: str) -> None:
        self.users[user_id].block()

    async def unban_user(self, user_id: str) -> None:
        self.users[user_id].unblock()

    async def promote_user(self, user_id: str) -> None:
        self.users[user_id].promote()

    async def demote_user(self, user_id: str) -> None:
        self.users[user_id].demote()

    async def is_user_banned(self, user_id: str) -> bool:
        return self.users[user_id].is_blocked

    async def update_activity(self, user_id: str) -> None:
        self.users[user_id].last_activity = datetime.datetime.now(datetime.UTC)

    async def get_last_users(self, time_span: datetime.timedelta) -> list[User]:
        return list(self.users.values())

    async def get_moderators(self) -> list[User]:
        return [u for u in self.users.values() if u.is_moderator]


class InMemorySubscriptions:
    def __init__(self) -> None:
        self.subscriptions: list[Subscription] = []

    async def get_user_subscriptions(self, user_id: str) -> list[Subscription]:
        return [s for s in self.subscriptions if s.user_id == user_id]

    async def get_all_subscriptions(self) -> list[Subscription]:
        return list(self.subscriptions)

    async def get_by_id(self, subscription_id: uuid.UUID) -> Subscription | None:
        return next((s for s in self.subscriptions if s.id == subscription_id), None)

    async def add_subscription(self, subscription: Subscription) -> None:
        self.subscriptions.append(subscription)

    async def remove_subscription(self, subscription: Subscription) -> None:
        self.subscriptions.remove(subscription)

    async def subscription_exists(self, user_id: str, details: SubscriptionDetails) -> bool:
        return any(s.details == details for s in await self.get_user_subscriptions(user_id))

    async def get_subscription_count(self, user_id: str) -> int:
        return len(await self.get_user_subscriptions(user_id))

    async def update_subscription(self, subscription: Subscription) -> None:
        pass

    async def reset_subscription(self, subscription: Subscription) -> None:
        pass


class InMemoryFavorites:
    def __init__(self) -> None:
        self.favorites: list[Favorite] = []

    async def get_favorites(self, user_id: str) -> list[Favorite]:
        return [f for f in self.favorites if f.user_id == user_id]

    async def add_favorite(self, favorite: Favorite) -> None:
        self.favorites.append(favorite)

    async def remove_favorite(self, favorite: Favorite) -> None:
        for stored in list(self.favorites):
            if stored.id == favorite.id:
                self.favorites.remove(stored)
                return

    async def favorite_exists(self, user_id: str, train: Train) -> bool:
        return any(f.train_info == train for f in await self.get_favorites(user_id))


class InMemoryNotifications:
    def __init__(self) -> None:
        self.notifications: list[Notification] = []

    async def pop_all(self) -> list[Notification]:
        result = self.notifications
        self.notifications = []
        return result

    async def add_notification(self, notification: Notification) -> None:
        self.notifications.append(notification)


class NoopMessages:
    async def add_message(self, message) -> None: ...
    async def get_user_messages(self, user_id: str) -> list: ...
    async def get_all_messages(self) -> list: ...


class NoopRw:
    async def get_stations(self, prefix: str) -> list[Station]:
        return []

    async def get_trains(self, route) -> list[Train]:
        return []

    async def get_seats(self, details) -> list[Car]:
        return []


@pytest.fixture
def facade() -> tuple[Facade, InMemoryUsers, InMemorySubscriptions, InMemoryFavorites]:
    users = InMemoryUsers()
    subscriptions = InMemorySubscriptions()
    favorites = InMemoryFavorites()
    notifications = InMemoryNotifications()
    fac = Facade(
        users=users,
        subscriptions=subscriptions,
        favorites=favorites,
        notifications=notifications,
        messages=NoopMessages(),
        rw=NoopRw(),
    )
    return fac, users, subscriptions, favorites


async def test_subscribe_get_and_unsubscribe_flow(facade) -> None:
    fac, _users, subscriptions, _favorites = facade
    user_id = "1"
    await fac.authenticate_user(user_id)
    details = make_subscription()

    await fac.subscribe(user_id, details)
    assert await fac.get_subscriptions(user_id, user_id) == [details]

    await fac.unsubscribe(user_id, details)
    assert await fac.get_subscriptions(user_id, user_id) == []
    assert await subscriptions.get_user_subscriptions(user_id) == []

    with pytest.raises(InvalidOperationError):
        await fac.unsubscribe(user_id, details)


async def test_subscription_limit_exceeded_raises_overflow(facade) -> None:
    fac, users, _subscriptions, _favorites = facade
    await fac.authenticate_user("user1")
    users.users["user1"].change_subscriptions_limits(1)

    await fac.subscribe("user1", make_subscription(datetime.date(2026, 8, 22)))
    with pytest.raises(OverflowError):
        await fac.subscribe("user1", make_subscription(datetime.date(2026, 8, 23)))


async def test_favorites_add_and_remove_flow(facade) -> None:
    fac, _users, _subscriptions, _favorites = facade
    await fac.authenticate_user("user1")
    train = make_train()

    assert await fac.is_in_favorites("user1", train) is False
    await fac.add_to_favorites("user1", train)
    assert await fac.is_in_favorites("user1", train) is True
    assert await fac.get_favorites("user1") == [train]

    await fac.remove_from_favorites("user1", train)
    assert await fac.is_in_favorites("user1", train) is False

    with pytest.raises(KeyNotFoundError):
        await fac.remove_from_favorites("user1", train)


async def test_unknown_user_is_rejected(facade) -> None:
    fac, _users, _subscriptions, _favorites = facade
    with pytest.raises(KeyNotFoundError):
        await fac.subscribe("ghost", make_subscription())
