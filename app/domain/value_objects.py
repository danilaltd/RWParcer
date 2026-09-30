"""Value objects, mirroring ``RWParcerCore.Domain.ValueObjects``.

Equality semantics follow the original ``ValueObject`` base class (all
components compared); ``Car`` compares free seats as an ordered set, exactly
like ``CarVO.GetEqualityComponents``.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import TYPE_CHECKING

from app.domain import times

if TYPE_CHECKING:
    import datetime
    import uuid


class CarType(enum.IntEnum):
    """C# ``enum CarType { Common = 1 .. SV = 6 }``."""

    COMMON = 1
    SEAT = 2
    PLATZKART = 3
    COUPE = 4
    SOFT = 5
    SV = 6

    @property
    def name_key(self) -> str:
        """The exact member name the C# ``ToString()`` produced in JSON."""
        return _PY_NAME_TO_CS_NAME[self]


_CAR_TYPE_CS_NAMES = {
    CarType.COMMON: "Common",
    CarType.SEAT: "Seat",
    CarType.PLATZKART: "Platzkart",
    CarType.COUPE: "Coupe",
    CarType.SOFT: "Soft",
    CarType.SV: "SV",
}
_PY_NAME_TO_CS_NAME = dict(_CAR_TYPE_CS_NAMES)
_CAR_TYPE_RU_LABELS = {
    CarType.COMMON: "Общий вагон",
    CarType.SEAT: "Сидячий вагон",
    CarType.PLATZKART: "Плацкартный вагон",
    CarType.COUPE: "Купейный вагон",
    CarType.SOFT: "Мягкий вагон",
    CarType.SV: "Вагон СВ",
}


def car_type_label(car_type: CarType) -> str:
    """C# ``Convert(CarType)`` switch used by the notifier."""
    return _CAR_TYPE_RU_LABELS.get(car_type, "Вагон неизвестного типа")


@dataclass(frozen=True)
class Station:
    """C# ``StationVO(label, exp)``."""

    label: str
    exp: str

    def __str__(self) -> str:  # pragma: no cover - debugging aid
        return self.label


@dataclass(frozen=True)
class Route:
    """C# ``RouteVO(from, to)`` — transient, never persisted."""

    from_station: Station
    to_station: Station


@dataclass(frozen=True)
class Train:
    """C# ``TrainVO``.

    ``from_time``/``to_time`` are *local* (Minsk, UTC+3) wall-clock times.
    """

    train_type: str
    train_number: str
    title_station_from: str
    title_station_to: str
    station_from: Station
    station_to: Station
    from_time: datetime.time
    to_time: datetime.time
    train_days: str
    train_days_except: str
    duration_minutes: int

    @classmethod
    def default(cls) -> Train:
        """Fallback used by the DB context when JSON decoding fails.

        Matches ``new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", "", 0)``.
        """
        return cls(
            train_type="default",
            train_number="0",
            title_station_from="",
            title_station_to="",
            station_from=Station("", ""),
            station_to=Station("", ""),
            from_time=times.unix_seconds_to_local_time(0),
            to_time=times.unix_seconds_to_local_time(0),
            train_days="",
            train_days_except="",
            duration_minutes=0,
        )


@dataclass(frozen=True)
class Car:
    """C# ``CarVO(type, number, freeSeats)``.

    Equality is order-insensitive over free seats, like the C# value object.
    """

    car_type: CarType
    number: int
    free_seats: tuple[int, ...] = ()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Car):
            return NotImplemented
        return (
            self.car_type == other.car_type
            and self.number == other.number
            and sorted(self.free_seats) == sorted(other.free_seats)
        )

    def __hash__(self) -> int:
        return hash((self.car_type, self.number, tuple(sorted(self.free_seats))))


@dataclass(frozen=True)
class SubscriptionDetails:
    """C# ``SubscriptionVO(train, date)``."""

    train: Train
    date: datetime.date


@dataclass(frozen=True)
class UserInfo:
    """C# ``UserVO``."""

    id: uuid.UUID
    is_moderator: bool
    max_subscriptions: int
    min_update_interval: int
    is_blocked: bool
    last_activity: datetime.datetime


@dataclass(frozen=True)
class MessageInfo:
    """C# ``MessageVO``."""

    sender_id: str
    receiver_id: str
    content: str
    sent_date: datetime.datetime


@dataclass(frozen=True)
class NotificationItem:
    """C# ``NotificationVO``."""

    user_id: uuid.UUID
    content: str
