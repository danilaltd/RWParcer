"""Round-trip tests for the session storage codecs (``app/bot/storage.py``).

No DB and no network: ``SessionRow`` is a lightweight fake and the SQLAlchemy
imports are exercised only through the pure codec functions.
"""

from __future__ import annotations

import datetime
import json
import uuid
from unittest.mock import MagicMock

from app.bot import storage
from app.bot.command_names import CommandNames
from app.bot.session import BotSession
from app.domain.value_objects import (
    Station,
    SubscriptionDetails,
    Train,
    UserInfo,
)
from app.infrastructure.db.models import SessionRow


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
        train_days="1,2,3",
        train_days_except="",
        duration_minutes=150,
    )


def make_subscription() -> SubscriptionDetails:
    return SubscriptionDetails(train=make_train(), date=datetime.date(2026, 8, 22))


def make_user() -> UserInfo:
    return UserInfo(
        id=uuid.uuid4(),
        is_moderator=False,
        max_subscriptions=5,
        min_update_interval=15,
        is_blocked=False,
        last_activity=datetime.datetime(2026, 8, 22, 12, 0),
    )


TS = datetime.timedelta(days=1, hours=2, minutes=3, seconds=5)


def test_timespan_codec_round_trip() -> None:
    serialized = storage._timespan_to_string(TS)
    assert serialized == "1.02:03:05"
    assert storage._timespan_from_string(serialized) == TS


def test_timespan_without_days_round_trip() -> None:
    span = datetime.timedelta(hours=4, minutes=5, seconds=6)
    assert storage._timespan_from_string(storage._timespan_to_string(span)) == span


def test_timespan_malformed_returns_none() -> None:
    assert storage._timespan_from_string("not a span") is None
    assert storage._timespan_from_string("1.2.3.4") is None


def test_train_round_trip_via_session_item() -> None:
    serialized = storage.to_session_data_item(make_train())
    assert serialized["Type"] == "Train"
    decoded = storage._item_data(serialized)
    assert decoded is not None
    assert decoded == make_train()


def test_station_round_trip_via_session_item() -> None:
    station = Station("Брест-Центральный", "БЦ")
    serialized = storage.to_session_data_item(station)
    assert serialized["Type"] == "Station"
    decoded = storage._item_data(serialized)
    assert decoded is not None
    assert decoded == station


def test_subscription_details_round_trip_via_session_item() -> None:
    subscription = make_subscription()
    serialized = storage.to_session_data_item(subscription)
    assert serialized["Type"] == "SubscriptionDetails"
    decoded = storage._item_data(serialized)
    assert decoded is not None
    assert decoded == subscription


def test_user_info_round_trip_via_session_item() -> None:
    user = make_user()
    serialized = storage.to_session_data_item(user)
    assert serialized["Type"] == "UserInfo"
    decoded = storage._item_data(serialized)
    assert decoded is not None
    assert decoded == user


def test_timedelta_round_trip_via_session_item() -> None:
    serialized = storage.to_session_data_item(TS)
    assert serialized["Type"] == "TimeSpan"
    assert storage._item_data(serialized) == TS


def test_list_round_trips_via_session_item() -> None:
    cases: list[tuple[list, str]] = [
        ([make_train()], "List[Train]"),
        ([Station("Минск", "МСК")], "List[Station]"),
        ([make_subscription()], "List[SubscriptionDetails]"),
        ([make_user()], "List[UserInfo]"),
    ]
    for items, expected_type in cases:
        serialized = storage.to_session_data_item(items)
        assert serialized["Type"] == expected_type
        decoded = storage._item_data(serialized)
        assert decoded is not None
        assert decoded == items


def test_bare_list_round_trip_via_session_item() -> None:
    serialized = storage.to_session_data_item([])
    assert serialized["Type"] == "List[Train]"
    assert storage._item_data(serialized) == []


def test_serialize_session_data_returns_json_array() -> None:
    session_data = [make_train(), make_user()]
    payload = storage.serialize_session_data(session_data)
    decoded = json.loads(payload)
    assert isinstance(decoded, list) and len(decoded) == 2
    assert decoded[0]["Type"] == "Train"
    assert decoded[1]["Type"] == "UserInfo"
    assert storage.SessionStorage._deserialize_data(payload) == session_data


def test_session_from_row_round_trips_data_json() -> None:
    session = BotSession(
        current_command=CommandNames.TRAIN_SELECT,
        init_state=True,
        data=[make_train(), Station("Минск", "МСК")],
        date=datetime.date(2026, 8, 22),
    )
    row = SessionRow(
        chat_id="1",
        current_command=(
            int(session.current_command) if session.current_command is not None else None
        ),
        init_state=True,
        data=storage.serialize_session_data(session.data),
        date=session.date,
    )
    decoded = storage.SessionStorage(MagicMock())._session_from_row(row)
    assert decoded.current_command == CommandNames.TRAIN_SELECT
    assert decoded.init_state is True
    assert decoded.data == session.data
    assert decoded.date == session.date
