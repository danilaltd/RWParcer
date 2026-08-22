"""Entities, mirroring ``RWParcerCore.Domain.Entities``.

Python dataclasses are mutable where the C# ones are mutable and otherwise
mirror the constructors. ``id`` fields keep the original ``Guid`` type as
``uuid.UUID``.
"""

from __future__ import annotations

import datetime
import uuid
from dataclasses import dataclass, field

from app.domain.value_objects import Car, SubscriptionDetails, Train


@dataclass
class User:
    """C# ``User`` entity with its behaviour methods."""

    id: str
    is_moderator: bool = False
    max_subscriptions: int = 5
    min_subscriptions_interval: int = 15
    is_blocked: bool = False
    last_activity: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    def block(self) -> None:
        self.is_blocked = True
        self.is_moderator = False

    def unblock(self) -> None:
        self.is_blocked = False

    def change_subscriptions_limits(self, max_subscriptions: int) -> None:
        self.max_subscriptions = max_subscriptions

    def change_interval_limits(self, interval: int) -> None:
        self.min_subscriptions_interval = interval

    def promote(self) -> None:
        self.is_blocked = False
        self.is_moderator = True

    def demote(self) -> None:
        self.is_moderator = False


@dataclass
class Subscription:
    """C# ``Subscription`` aggregate.

    ``details`` is the persisted ``SubscriptionVO``;
    ``last_state`` was persisted as a JSONB array of cars.
    """

    id: uuid.UUID
    user_id: str
    details: SubscriptionDetails
    last_update: datetime.datetime | None = None
    last_state: list[Car] = field(default_factory=list)


@dataclass(frozen=True)
class Notification:
    """C# ``Notification``."""

    id: uuid.UUID
    user_id: str
    content: str


@dataclass
class Message:
    """C# ``Message``."""

    id: uuid.UUID
    sender_id: str
    receiver_id: str
    content: str
    sent_date: datetime.datetime = field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )


@dataclass(frozen=True)
class Favorite:
    """C# ``Favorite``."""

    id: uuid.UUID
    user_id: str
    train_info: Train
