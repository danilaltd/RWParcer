"""JSON codecs with the *exact* shapes produced by the EF value converters.

Each ``*_to_json`` returns a JSON-python dict in the same key order the C#
``Utf8JsonWriter`` used; each ``*_from_json`` parses it back. The fallback
behaviour of ``AppDbContext`` (invalid train/subscription -> default value) is
exposed as ``*_from_json_or_default`` helpers.
"""

from __future__ import annotations

import datetime
import logging
import uuid
from typing import TYPE_CHECKING, Any

from app.domain import times
from app.domain.value_objects import (
    Car,
    CarType,
    MessageInfo,
    NotificationItem,
    Route,
    Station,
    SubscriptionDetails,
    Train,
    UserInfo,
)

if TYPE_CHECKING:
    from app.domain.entities import Message

logger = logging.getLogger(__name__)


class CodecError(ValueError):
    """Raised when persisted JSON cannot be decoded (like ``JsonException``)."""


# ---------------------------------------------------------------------------
# Station
# ---------------------------------------------------------------------------


def station_to_json(station: Station) -> dict[str, Any]:
    return {"label": station.label, "exp": station.exp}


def station_from_json(data: Any) -> Station:
    if not isinstance(data, dict) or "label" not in data or "exp" not in data:
        raise CodecError("Invalid station JSON")
    return Station(label=str(data["label"]), exp=str(data["exp"]))


def route_to_json(route: Route) -> dict[str, Any]:
    return {"from": station_to_json(route.from_station), "to": station_to_json(route.to_station)}


def route_from_json(data: Any) -> Route:
    if not isinstance(data, dict) or "from" not in data or "to" not in data:
        raise CodecError("Invalid route JSON")
    return Route(
        from_station=station_from_json(data["from"]),
        to_station=station_from_json(data["to"]),
    )


# ---------------------------------------------------------------------------
# Train
# ---------------------------------------------------------------------------


def train_to_json(train: Train) -> dict[str, Any]:
    """Serialize in the same order as ``TrainVOConverter.Write``."""
    return {
        "trainType": train.train_type,
        "trainNumber": train.train_number,
        "trainDays": train.train_days,
        "trainDaysExcept": train.train_days_except,
        "fromTime": times.local_time_to_storage(train.from_time),
        "toTime": times.local_time_to_storage(train.to_time),
        "durationMinutes": train.duration_minutes,
        "main_station_from": station_to_json(train.main_station_from),
        "main_station_to": station_to_json(train.main_station_to),
        "stationFrom": station_to_json(train.station_from),
        "stationTo": station_to_json(train.station_to),
    }


def train_from_json(data: Any) -> Train:
    if not isinstance(data, dict):
        raise CodecError("Invalid train JSON (not an object)")
    try:
        return Train(
            train_type=str(data["trainType"]),
            train_number=str(data["trainNumber"]),
            train_days=str(data["trainDays"]),
            train_days_except=str(data["trainDaysExcept"]),
            from_time=times.storage_string_to_local_time(str(data["fromTime"])),
            to_time=times.storage_string_to_local_time(str(data["toTime"])),
            duration_minutes=int(data["durationMinutes"]),
            main_station_from=station_from_json(data["main_station_from"]),
            main_station_to=station_from_json(data["main_station_to"]),
            station_from=station_from_json(data["stationFrom"]),
            station_to=station_from_json(data["stationTo"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise CodecError(f"Invalid train JSON: {exc}") from exc


def train_from_json_or_default(data: Any) -> Train:
    """``AppDbContext.DeserializeTrainVO``: on error log and return default."""
    try:
        return train_from_json(data)
    except CodecError as exc:
        logger.debug("Deserialization error for TrainVO: %s", exc)
        return Train.default()


# ---------------------------------------------------------------------------
# Car
# ---------------------------------------------------------------------------


def car_to_json(car: Car) -> dict[str, Any]:
    return {
        "type": car.car_type.name_key,
        "number": car.number,
        "freeSeats": list(car.free_seats),
    }


def car_from_json(data: Any) -> Car:
    if not isinstance(data, dict) or not {"type", "number", "freeSeats"} <= data.keys():
        raise CodecError("Invalid car JSON")
    raw_type = str(data["type"])
    if raw_type in _CAR_TYPE_BY_NAME:
        car_type = _CAR_TYPE_BY_NAME[raw_type]
    else:
        try:
            car_type = CarType(int(raw_type))
        except ValueError as exc:
            raise CodecError(f"Invalid CarType value: {raw_type}") from exc
    seats_raw = data["freeSeats"]
    if not isinstance(seats_raw, list):
        raise CodecError("Expected 'freeSeats' to be an array")
    try:
        seats = tuple(int(seat) for seat in seats_raw)
        number = int(data["number"])
    except (TypeError, ValueError) as exc:
        raise CodecError(f"Invalid car numbers: {exc}") from exc
    return Car(car_type=car_type, number=number, free_seats=seats)


_CAR_TYPE_BY_NAME: dict[str, CarType] = {}
for _member in CarType:
    _CAR_TYPE_BY_NAME[_member.name_key] = _member
    _CAR_TYPE_BY_NAME[_member.name_key.lower()] = _member
    _CAR_TYPE_BY_NAME[str(int(_member))] = _member


def cars_from_json_or_default(data: Any) -> list[Car]:
    """``Deserialize<List<CarVO>> ?? new()`` — tolerate anything corrupt."""
    if not isinstance(data, list):
        logger.debug("Invalid car state JSON, returning []")
        return []
    result: list[Car] = []
    for item in data:
        try:
            result.append(car_from_json(item))
        except CodecError as exc:
            logger.debug("Skipping invalid car JSON: %s", exc)
    return result


# ---------------------------------------------------------------------------
# Subscription details
# ---------------------------------------------------------------------------


def subscription_details_to_json(details: SubscriptionDetails) -> dict[str, Any]:
    return {"date": details.date.isoformat(), "train": train_to_json(details.train)}


def subscription_details_from_json(data: Any) -> SubscriptionDetails:
    if not isinstance(data, dict) or "date" not in data or "train" not in data:
        raise CodecError("Invalid subscription JSON")
    try:
        date = datetime.date.fromisoformat(str(data["date"]))
    except ValueError as exc:
        raise CodecError(f"Invalid date format: {data['date']}") from exc
    return SubscriptionDetails(date=date, train=train_from_json(data["train"]))


def subscription_details_from_json_or_default(data: Any) -> SubscriptionDetails:
    """``AppDbContext.DeserializeSubscriptionVO`` fallback."""
    try:
        return subscription_details_from_json(data)
    except CodecError as exc:
        logger.debug("Deserialization error for SubscriptionVO: %s", exc)
        return SubscriptionDetails(train=Train.default(), date=datetime.date.today())


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


def user_to_json(user: UserInfo) -> dict[str, Any]:
    return {
        "id": str(user.id),
        "telegramUserId": user.telegram_user_id,
        "username": user.username,
        "displayName": user.display_name,
        "isModerator": user.is_moderator,
        "maxSubscriptions": user.max_subscriptions,
        "minSubscriptionsInterval": user.min_update_interval,
        "isBlocked": user.is_blocked,
        "lastActivity": user.last_activity.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def user_from_json(data: Any) -> UserInfo:
    if not isinstance(data, dict):
        raise CodecError("Invalid user JSON")
    required = (
        "id",
        "telegramUserId",
        "username",
        "displayName",
        "isModerator",
        "maxSubscriptions",
        "minSubscriptionsInterval",
        "isBlocked",
        "lastActivity",
    )
    if any(key not in data for key in required):
        raise CodecError("Invalid user JSON (missing fields)")
    try:
        return UserInfo(
            id=uuid.UUID(data["id"]),
            telegram_user_id=int(data["telegramUserId"]),
            username=data["username"],
            display_name=data["displayName"],
            is_moderator=bool(data["isModerator"]),
            max_subscriptions=int(data["maxSubscriptions"]),
            min_update_interval=int(data["minSubscriptionsInterval"]),
            is_blocked=bool(data["isBlocked"]),
            last_activity=datetime.datetime.fromisoformat(str(data["lastActivity"])),
        )
    except (TypeError, ValueError) as exc:
        raise CodecError(f"Invalid user JSON: {exc}") from exc


# ---------------------------------------------------------------------------
# Message
# ---------------------------------------------------------------------------


def message_to_json(message: Message) -> dict[str, Any]:
    return {
        "senderId": message.sender_id,
        "receiverId": message.receiver_id,
        "content": message.content,
        "sentDate": message.sent_date.strftime("%Y-%m-%dT%H:%M:%S"),
    }


def message_from_json(data: Any) -> MessageInfo:
    if not isinstance(data, dict):
        raise CodecError("Invalid message JSON")
    required = ("senderId", "receiverId", "content", "sentDate")
    if any(key not in data for key in required):
        raise CodecError("Invalid message JSON (missing fields)")
    try:
        return MessageInfo(
            sender_id=str(data["senderId"]),
            receiver_id=str(data["receiverId"]),
            content=str(data["content"]),
            sent_date=datetime.datetime.fromisoformat(str(data["sentDate"])),
        )
    except (TypeError, ValueError) as exc:
        raise CodecError(f"Invalid message JSON: {exc}") from exc


def notification_to_json(item: NotificationItem) -> dict[str, Any]:
    # used by tests only
    return {"userId": item.user_id, "content": item.content}
