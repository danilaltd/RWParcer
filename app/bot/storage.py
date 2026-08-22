"""Session persistence, mirroring ``PostgresSessionStore`` + ``SessionManager``.

The C# bot keeps the whole FSM in memory (``ConcurrentDictionary``) and
rewrites the full ``sessions`` table after every update. This module does the
same against the existing async SQLAlchemy infrastructure:

* ``SessionStorage.load()`` reads every ``SessionRow`` and decodes the ``data``
  column (``[{"Type": ..., "Data": ...}, ...]`` — the shape
  ``PostgresSessionStore.SaveAsync`` produced via ``SerializeToJson``);
* ``SessionStorage.save_all()`` writes a full snapshot of the in-memory
  sessions, upserting each row, identical to ``SaveAsync``;
* ``BotSessionManager`` is the Python twin of ``SessionManager`` — a
  ``dict``-backed ``GetOrAdd`` store keyed by chat id.

When the DB is unavailable the storage degrades to an in-memory-only store
(load returns an empty manager and saves are no-ops), preserving the C#
fallback behaviour of ``_store = store.Load()`` never crashing startup.
"""

from __future__ import annotations

import asyncio
import datetime
import json
import logging
from typing import Any

from app.bot.command_names import command_name_by_value
from app.bot.session import BotSession
from app.domain import json_codecs
from app.domain.value_objects import Station, SubscriptionDetails, Train, UserInfo
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

logger = logging.getLogger(__name__)

SESSION_TYPE_KEY = "Type"
SESSION_DATA_KEY = "Data"

# Type tags used in the ``sessions.data`` payload. They only need to
# round-trip within this store (the C# used ``AssemblyQualifiedName``).
TAG_LIST_TRAIN = "List[Train]"
TAG_LIST_STATION = "List[Station]"
TAG_LIST_SUBSCRIPTION = "List[SubscriptionDetails]"
TAG_LIST_USER = "List[UserInfo]"
TAG_TRAIN = "Train"
TAG_STATION = "Station"
TAG_SUBSCRIPTION = "SubscriptionDetails"
TAG_USER = "UserInfo"
TAG_TIMESPAN = "TimeSpan"


# ---------------------------------------------------------------------------
# Individual value-object codecs
# ---------------------------------------------------------------------------

def _timespan_to_string(span: datetime.timedelta) -> str:
    """Mirror ``System.Text.Json`` default ``TimeSpan`` serialization."""
    total_seconds = int(span.total_seconds())
    days, rest = divmod(total_seconds, 86400)
    hours, rest = divmod(rest, 3600)
    minutes, seconds = divmod(rest, 60)
    time_part = f"{hours:02}:{minutes:02}:{seconds:02}"
    return f"{days}.{time_part}" if days else time_part


def _timespan_from_string(value: str) -> datetime.timedelta | None:
    parts = value.split(".")
    if len(parts) == 2:
        try:
            days = int(parts[0])
        except ValueError:
            return None
        time_part = parts[1]
    elif len(parts) == 1:
        days = 0
        time_part = parts[0]
    else:
        return None
    segments = time_part.split(":")
    try:
        if len(segments) == 3:
            hours, minutes, seconds = (int(s) for s in segments)
        elif len(segments) == 2:
            hours, minutes = (int(s) for s in segments)
            seconds = 0
        elif len(segments) == 1:
            return datetime.timedelta(days=days, seconds=int(segments[0]))
        else:
            return None
    except ValueError:
        return None
    return datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def to_session_data_item(item: Any) -> dict[str, str]:
    """``{"Type": ..., "Data": json}`` — ``PostgresSessionStore.SaveAsync``."""
    if isinstance(item, list):
        if item and all(isinstance(x, Train) for x in item):
            data = [json_codecs.train_to_json(x) for x in item]
            return {"Type": TAG_LIST_TRAIN, "Data": json.dumps(data, ensure_ascii=False)}
        if item and all(isinstance(x, Station) for x in item):
            data = [json_codecs.station_to_json(x) for x in item]
            return {"Type": TAG_LIST_STATION, "Data": json.dumps(data, ensure_ascii=False)}
        if item and all(isinstance(x, SubscriptionDetails) for x in item):
            data = [json_codecs.subscription_details_to_json(x) for x in item]
            return {
                "Type": TAG_LIST_SUBSCRIPTION,
                "Data": json.dumps(data, ensure_ascii=False),
            }
        if item and all(isinstance(x, UserInfo) for x in item):
            data = [json_codecs.user_to_json(x) for x in item]
            return {"Type": TAG_LIST_USER, "Data": json.dumps(data, ensure_ascii=False)}
        # A bare/empty list has no element type to decode back into; persist
        # as empty so reloading yields the same empty list.
        return {"Type": TAG_LIST_TRAIN, "Data": json.dumps(list(item), ensure_ascii=False)}

    if isinstance(item, Train):
        return {
            "Type": TAG_TRAIN,
            "Data": json.dumps(json_codecs.train_to_json(item), ensure_ascii=False),
        }
    if isinstance(item, Station):
        return {
            "Type": TAG_STATION,
            "Data": json.dumps(json_codecs.station_to_json(item), ensure_ascii=False),
        }
    if isinstance(item, SubscriptionDetails):
        return {
            "Type": TAG_SUBSCRIPTION,
            "Data": json.dumps(
                json_codecs.subscription_details_to_json(item), ensure_ascii=False
            ),
        }
    if isinstance(item, UserInfo):
        return {
            "Type": TAG_USER,
            "Data": json.dumps(json_codecs.user_to_json(item), ensure_ascii=False),
        }
    if isinstance(item, datetime.timedelta):
        return {"Type": TAG_TIMESPAN, "Data": _timespan_to_string(item)}
    logger.debug("Unsupported session data item %s, skipping", type(item))
    return {"Type": TAG_TIMESPAN, "Data": "00:00:00"}


def _json_array(json_data: str) -> list:
    if not isinstance(json_data, str):
        return []
    try:
        parsed = json.loads(json_data)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def serialize_session_data(data: list[Any]) -> str:
    """``JsonSerializer.Serialize(jsonObjects)`` for one session's payload."""
    return json.dumps(
        [to_json_data_item(item) for item in data],
        ensure_ascii=False,
    )


def to_json_data_item(item: Any) -> dict[str, str]:
    return to_session_data_item(item)


class SessionStorage:
    """Port of ``PostgresSessionStore`` + ``ISessionStore`` contract.

    Uses the *same* ``async_sessionmaker`` as the repositories (``core_db``).
    ``None`` ``session_factory`` selects the in-memory fallback mode.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession] | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._save_lock = asyncio.Lock()

    @property
    def available(self) -> bool:
        return self._session_factory is not None

    async def load(self) -> dict[str, BotSession]:
        """Read the ``sessions`` table — ``PostgresSessionStore.Load()``."""
        sessions: dict[str, BotSession] = {}
        if self._session_factory is None:
            return sessions
        try:
            async with self._session_factory() as db_session:
                rows = (
                    (await db_session.execute(select(SessionRow))).scalars().all()
                )
        except Exception as exc:  # noqa: BLE001 - degrade to in-memory store
            logger.warning("Failed to load sessions, using empty store: %s", exc)
            return sessions

        for row in rows:
            sessions[row.chat_id] = self._session_from_row(row)
        return sessions

    def _session_from_row(self, row: SessionRow) -> BotSession:
        if not row.data:
            return BotSession(
                current_command=command_name_by_value(row.current_command),
                init_state=bool(row.init_state),
                data=[],
                date=row.date,
            )
        try:
            data = self._deserialize_data(row.data)
            return BotSession(
                current_command=command_name_by_value(row.current_command),
                init_state=bool(row.init_state),
                data=data,
                date=row.date,
            )
        except Exception as exc:  # noqa: BLE001 - C# fallback to empty data
            logger.warning(
                "Error deserializing session data for chat %s: %s",
                row.chat_id,
                exc,
            )
            return BotSession(
                current_command=command_name_by_value(row.current_command),
                init_state=bool(row.init_state),
                data=[],
                date=row.date,
            )

    @staticmethod
    def _deserialize_data(raw: str) -> list[Any]:
        if not raw:
            return []
        items = json.loads(raw)
        if not isinstance(items, list):
            return []
        data: list[Any] = []
        for item in items:
            decoded = _item_data(item)
            if decoded is not None:
                data.append(decoded)
        return data

    async def save_all(self, sessions: dict[str, BotSession]) -> None:
        """Full-table snapshot — ``PostgresSessionStore.SaveAsync()``."""
        if self._session_factory is None:
            return
        async with self._save_lock, self._session_factory() as db_session:
            existing_rows = {
                row.chat_id: row
                for row in (
                    (await db_session.execute(select(SessionRow))).scalars().all()
                )
            }
            for chat_id, bot_session in sessions.items():
                values = {
                    "current_command": (
                        int(bot_session.current_command)
                        if bot_session.current_command is not None
                        else None
                    ),
                    "init_state": bool(bot_session._init_state),
                    "data": serialize_session_data(bot_session.data),
                    "date": bot_session.date,
                }
                if chat_id in existing_rows:
                    existing = existing_rows[chat_id]
                    existing.current_command = values["current_command"]
                    existing.init_state = values["init_state"]
                    existing.data = values["data"]
                    existing.date = values["date"]
                else:
                    db_session.add(SessionRow(chat_id=chat_id, **values))
            await db_session.commit()


class BotSessionManager:
    """Python twin of ``SessionManager`` (``GetOrAdd`` by chat id)."""

    def __init__(
        self, store: dict[str, BotSession] | None = None
    ) -> None:
        self._store: dict[str, BotSession] = store if store is not None else {}

    def get_session(self, chat_id: str) -> BotSession:
        session = self._store.get(chat_id)
        if session is None:
            session = BotSession()
            self._store[chat_id] = session
        return session

    def get_all_sessions(self) -> dict[str, BotSession]:
        return self._store


def _item_data(item: Any) -> Any | None:
    """Decode a single payload item, ``None`` for unreadable types."""
    if not isinstance(item, dict):
        return None
    type_name = item.get("Type")
    json_data = item.get("Data")
    if type_name is None or json_data is None:
        return None
    if type_name == TAG_LIST_TRAIN:
        return [
            json_codecs.train_from_json_or_default(x)
            for x in _json_array(json_data)
        ]
    if type_name == TAG_LIST_STATION:
        return [json_codecs.station_from_json(x) for x in _json_array(json_data)]
    if type_name == TAG_LIST_SUBSCRIPTION:
        return [
            json_codecs.subscription_details_from_json_or_default(x)
            for x in _json_array(json_data)
        ]
    if type_name == TAG_LIST_USER:
        return [json_codecs.user_from_json(x) for x in _json_array(json_data)]
    if type_name == TAG_TIMESPAN:
        return _timespan_from_string(json_data)
    obj = _json_object(json_data)
    if obj is None:
        return None
    try:
        if type_name == TAG_TRAIN:
            return json_codecs.train_from_json(obj)
        if type_name == TAG_STATION:
            return json_codecs.station_from_json(obj)
        if type_name == TAG_SUBSCRIPTION:
            return json_codecs.subscription_details_from_json(obj)
        if type_name == TAG_USER:
            return json_codecs.user_from_json(obj)
    except Exception as exc:  # noqa: BLE001 - C# ``catch (Exception)``
        logger.debug("Skipping invalid session item %s: %s", type_name, exc)
    return None


def _json_object(json_data: Any) -> dict | None:
    if not isinstance(json_data, str):
        return None
    try:
        parsed = json.loads(json_data)
    except (json.JSONDecodeError, TypeError):
        return None
    return parsed if isinstance(parsed, dict) else None





from app.infrastructure.db.models import SessionRow  # noqa: E402
