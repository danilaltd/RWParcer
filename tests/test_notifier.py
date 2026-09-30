"""Unit tests for ``app/application/notifier.py``.

No network and no real DB: repositories are plain Protocol fakes driving the
``Notifier`` through the real ``_process_subscription``/diff logic.
"""

from __future__ import annotations

import datetime
import uuid

from app.application.notifier import Notifier
from app.domain.entities import Notification, Subscription, User
from app.domain.value_objects import (
    Car,
    CarType,
    Route,
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


class FakeUsers:
    def __init__(self, min_interval: int = 0) -> None:
        self._min_interval = min_interval

    async def register_user(
        self, telegram_user_id: int, telegram_chat_id: int, username: str | None, display_name: str
    ) -> User:
        raise NotImplementedError

    async def get_user_min_interval(self, user_id: uuid.UUID) -> int:
        return self._min_interval

    async def is_user_registered(self, user_id: uuid.UUID) -> bool:
        raise NotImplementedError

    async def add_user(self, user: User) -> None:
        raise NotImplementedError

    async def is_user_moderator(self, user_id: uuid.UUID) -> bool:
        raise NotImplementedError

    async def get_user_max_subscriptions(self, user_id: uuid.UUID) -> int:
        raise NotImplementedError

    async def get_user_by_id(self, user_id: uuid.UUID) -> None:
        raise NotImplementedError

    async def set_users_min_interval(self, user_id: uuid.UUID, min_interval: int) -> None:
        raise NotImplementedError

    async def set_users_max_subscriptions(self, user_id: uuid.UUID, max_subscriptions: int) -> None:
        raise NotImplementedError

    async def ban_user(self, user_id: uuid.UUID) -> None:
        raise NotImplementedError

    async def unban_user(self, user_id: uuid.UUID) -> None:
        raise NotImplementedError

    async def promote_user(self, user_id: uuid.UUID) -> None:
        raise NotImplementedError

    async def demote_user(self, user_id: uuid.UUID) -> None:
        raise NotImplementedError

    async def is_user_banned(self, user_id: uuid.UUID) -> bool:
        raise NotImplementedError

    async def update_activity(self, user_id: uuid.UUID) -> None:
        raise NotImplementedError

    async def get_last_users(self, time_span: datetime.timedelta) -> list:
        raise NotImplementedError

    async def get_moderators(self) -> list:
        raise NotImplementedError


class FakeSubscriptions:
    def __init__(self, actual: Subscription) -> None:
        self._actual = actual
        self.updated: list[Subscription] = []

    async def claim_due_subscriptions(self, limit: int = 10) -> list[Subscription]:
        return []

    async def get_by_id(self, subscription_id: uuid.UUID) -> Subscription | None:
        return self._actual

    async def update_subscription(self, subscription: Subscription) -> None:
        self.updated.append(subscription)

    async def save_availability_snapshot(self, subscription_id: uuid.UUID, cars: list[Car]) -> bool:
        return True

    async def get_all_subscriptions(self) -> list[Subscription]:
        return []

    async def get_user_subscriptions(self, user_id: uuid.UUID) -> list[Subscription]:
        raise NotImplementedError

    async def add_subscription(self, subscription: Subscription) -> None:
        raise NotImplementedError

    async def remove_subscription(self, subscription: Subscription) -> None:
        raise NotImplementedError

    async def subscription_exists(
        self, user_id: uuid.UUID, service_route_id: uuid.UUID, target_date: datetime.date
    ) -> bool:
        raise NotImplementedError

    async def get_subscription_count(self, user_id: uuid.UUID) -> int:
        raise NotImplementedError

    async def reset_subscription(self, subscription: Subscription) -> None:
        raise NotImplementedError


class FakeNotifications:
    def __init__(self) -> None:
        self.added: list[Notification] = []

    async def add_notification(self, notification: Notification) -> None:
        self.added.append(notification)

    async def claim_pending_notifications(self, limit: int = 50) -> list[Notification]:
        result = self.added
        self.added = []
        return result

    async def mark_sent(self, notification_id: uuid.UUID) -> None:
        pass

    async def mark_failed(self, notification_id: uuid.UUID, error_text: str) -> None:
        pass


class FakeRw:
    def __init__(self, seats: list[Car]) -> None:
        self._seats = seats

    async def get_seats(self, details: SubscriptionDetails) -> list[Car]:
        return self._seats

    async def get_stations(self, prefix: str) -> list[Station]:
        raise NotImplementedError

    async def get_trains(self, route: Route) -> list[Train]:
        raise NotImplementedError


class _QuietLogger:
    def debug(self, message: str) -> None: ...
    def info(self, message: str) -> None: ...
    def warning(self, message: str) -> None: ...
    def error(self, message: str) -> None: ...


def make_notifier(
    actual: Subscription,
    seats: list[Car],
    subscriptions: FakeSubscriptions | None = None,
    notifications: FakeNotifications | None = None,
    users: FakeUsers | None = None,
) -> tuple[Notifier, FakeSubscriptions, FakeNotifications]:
    subs = subscriptions or FakeSubscriptions(actual)
    notifs = notifications or FakeNotifications()
    notifier = Notifier(
        subscriptions=subs,
        notifications=notifs,
        users=users or FakeUsers(),
        rw=FakeRw(seats),
        logger=_QuietLogger(),
    )
    return notifier, subs, notifs


async def test_seat_changed_uses_izmneny_mesta_exact_message() -> None:
    details = SubscriptionDetails(train=make_train(), date=datetime.date(2026, 8, 22))
    old_state = [Car(car_type=CarType.COUPE, number=1, free_seats=(1, 2, 3))]
    uid = uuid.uuid4()
    sub = Subscription(
        id=uuid.uuid4(),
        user_id=uid,
        details=details,
        last_update=None,
        last_state=old_state,
    )
    new_state = [Car(car_type=CarType.COUPE, number=1, free_seats=(1, 2))]
    notifier, subs, notifs = make_notifier(sub, new_state)

    await notifier._process_subscription(sub)

    assert len(notifs.added) == 1
    expected = (
        "22.08.2026\n"
        "Минск - Гомель\n"
        "08:00→10:30\n"
        "Изменены места: \n"
        "Купейный вагон №1: Заняты места 3"
    )
    assert notifs.added[0].content == expected
    assert notifs.added[0].user_id == sub.user_id
    assert subs.updated, "the refreshed state and last_update must be persisted"


async def test_unchanged_seats_produce_no_notification() -> None:
    details = SubscriptionDetails(train=make_train(), date=datetime.date(2026, 8, 22))
    state = [Car(car_type=CarType.COUPE, number=1, free_seats=(1, 2, 3))]
    uid = uuid.uuid4()
    sub = Subscription(
        id=uuid.uuid4(),
        user_id=uid,
        details=details,
        last_update=None,
        last_state=state,
    )
    notifier, subs, notifs = make_notifier(sub, list(state))

    await notifier._process_subscription(sub)

    assert notifs.added == []
    assert subs.updated, "last_update must be refreshed even when seats match"


async def test_svobodnye_mesta_fallback_when_no_previous_state() -> None:
    new_state = [Car(car_type=CarType.COUPE, number=1, free_seats=(5, 6))]
    uid = uuid.uuid4()
    sub = Subscription(
        id=uuid.uuid4(),
        user_id=uid,
        details=SubscriptionDetails(train=make_train(), date=datetime.date(2026, 8, 22)),
        last_update=None,
        last_state=None,
    )
    notifier, subs, notifs = make_notifier(sub, new_state)

    await notifier._process_subscription(sub)

    assert len(notifs.added) == 1
    assert "Свободные места" in notifs.added[0].content
    assert "Изменены места" not in notifs.added[0].content


def test_find_seat_changes_diffs_added_and_removed() -> None:
    old = [Car(car_type=CarType.COUPE, number=1, free_seats=(1, 2))]
    new = [
        Car(car_type=CarType.COUPE, number=1, free_seats=(2, 3)),
        Car(car_type=CarType.PLATZKART, number=4, free_seats=(10,)),
    ]
    changes = Notifier._find_seat_changes(old, new)

    assert any("Заняты места 1" in c for c in changes)
    assert any("Освобождены места 3" in c for c in changes)
    assert any("Новый вагон" in c for c in changes)
    assert changes == [
        "Купейный вагон №1: Заняты места 1",
        "Купейный вагон №1: Освобождены места 3",
        "Плацкартный вагон №4: Новый вагон, места 10",
    ]
