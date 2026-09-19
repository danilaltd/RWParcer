"""Entities, mirroring the normalized database schema and domain entities."""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.value_objects import Car, SubscriptionDetails, Train


@dataclass
class User:
    """Identity user entity."""

    id: uuid.UUID
    telegram_user_id: int
    telegram_chat_id: int
    username: str | None = None
    display_name: str | None = None
    is_moderator: bool = False
    max_subscriptions: int = 5
    min_subscriptions_interval: int = 15
    status: str = "ACTIVE"
    last_activity: datetime.datetime | None = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    @property
    def is_blocked(self) -> bool:
        return self.status == "BLOCKED"

    def block(self) -> None:
        self.status = "BLOCKED"
        self.is_moderator = False

    def unblock(self) -> None:
        self.status = "ACTIVE"

    def change_subscriptions_limits(self, max_subscriptions: int) -> None:
        self.max_subscriptions = max_subscriptions

    def change_interval_limits(self, interval: int) -> None:
        self.min_subscriptions_interval = interval

    def promote(self) -> None:
        self.status = "ACTIVE"
        self.is_moderator = True

    def demote(self) -> None:
        self.is_moderator = False


@dataclass
class Subscription:
    """Monitoring subscription aggregate."""

    id: uuid.UUID
    user_id: uuid.UUID
    details: SubscriptionDetails
    service_route_id: uuid.UUID = field(default_factory=uuid.uuid4)
    target_date: datetime.date = field(default_factory=datetime.date.today)
    status: str = "ACTIVE"
    last_update: datetime.datetime | None = None
    last_checked_at: datetime.datetime | None = None
    next_check_at: datetime.datetime | None = None
    last_state: list[Car] | None = None


def generate_notification_id() -> uuid.UUID:
    return uuid.uuid4()


@dataclass(frozen=True)
class Notification:
    """Messaging notification entity."""

    id: uuid.UUID
    user_id: uuid.UUID
    content: str
    subscription_id: uuid.UUID | None = None
    notification_type: str = "SEATS_CHANGED"
    status: str = "PENDING"
    available_at: datetime.datetime | None = None
    attempts: int = 0


@dataclass
class Message:
    """Messaging message entity."""

    id: uuid.UUID
    sender_id: uuid.UUID | None
    receiver_id: uuid.UUID | None
    content: str
    sent_date: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


@dataclass(frozen=True)
class Favorite:
    """Monitoring favorite entity."""

    id: uuid.UUID
    user_id: uuid.UUID
    service_route_id: uuid.UUID
    train_info: Train
