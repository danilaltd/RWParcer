"""Session persistence against ``bot.conversation_sessions`` table using asyncpg."""

from __future__ import annotations

import asyncio
import datetime
import json
import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import uuid
    from collections.abc import Mapping

    from app.infrastructure.db.pool import ConnectionPool

import aiosql
import aiosql.adapters.asyncpg
import aiosql.queries
from app.bot.command_names import command_name_by_value
from app.bot.session import BotSession
from app.domain import json_codecs
from app.domain.value_objects import Station, SubscriptionDetails, Train, UserInfo

logger = logging.getLogger(__name__)

TAG_LIST_TRAIN = "List[Train]"
TAG_LIST_STATION = "List[Station]"
TAG_LIST_SUBSCRIPTION = "List[SubscriptionDetails]"
TAG_LIST_USER = "List[UserInfo]"
TAG_TRAIN = "Train"
TAG_STATION = "Station"
TAG_SUBSCRIPTION = "SubscriptionDetails"
TAG_USER = "UserInfo"
TAG_TIMESPAN = "TimeSpan"


def _timespan_to_string(span: datetime.timedelta) -> str:
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
            "Data": json.dumps(json_codecs.subscription_details_to_json(item), ensure_ascii=False),
        }
    if isinstance(item, UserInfo):
        return {
            "Type": TAG_USER,
            "Data": json.dumps(json_codecs.user_to_json(item), ensure_ascii=False),
        }
    if isinstance(item, datetime.timedelta):
        return {"Type": TAG_TIMESPAN, "Data": _timespan_to_string(item)}
    return {"Type": TAG_TIMESPAN, "Data": "00:00:00"}


to_json_data_item = to_session_data_item


def _json_array(json_data: str) -> list:
    if not isinstance(json_data, str):
        return []
    try:
        parsed = json.loads(json_data)
    except json.JSONDecodeError:
        return []
    return parsed if isinstance(parsed, list) else []


def serialize_session_data(data: list[Any]) -> str:
    return json.dumps(
        [to_json_data_item(item) for item in data],
        ensure_ascii=False,
    )


def _load_queries(filename: str) -> aiosql.queries.Queries:
    import importlib.resources

    sql_text = (
        importlib.resources.files("app.infrastructure.db.queries").joinpath(filename).read_text()
    )
    return aiosql.from_str(sql_text, driver_adapter="asyncpg")


class SessionStorage:
    def __init__(
        self,
        pool: ConnectionPool,
    ) -> None:
        self._pool = pool
        self._save_lock = asyncio.Lock()

    async def load(self) -> dict[uuid.UUID, BotSession]:
        sessions: dict[uuid.UUID, BotSession] = {}
        try:
            async with self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
                query = (
                    "SELECT user_id, current_command_code, init_state, context, last_input_date "
                    "FROM bot.conversation_sessions"
                )
                rows = await conn.fetch(query)
        except Exception as exc:
            logger.warning("Failed to load sessions, using empty store: %s", exc)
            return sessions

        for row in rows:
            sessions[row["user_id"]] = self._session_from_row(row)
        return sessions

    def _session_from_row(self, row: Mapping[str, Any]) -> BotSession:
        decoded_data = self._deserialize_data(
            row["context"].get("data", []) if isinstance(row["context"], dict) else []
        )
        return BotSession(
            current_command=command_name_by_value(row["current_command_code"]),
            init_state=bool(row["init_state"]),
            data=decoded_data,
            date=row["last_input_date"] or datetime.date.today(),
        )

    @staticmethod
    def _deserialize_data(raw: Any) -> list[Any]:
        if not raw:
            return []
        if isinstance(raw, str):
            try:
                items = json.loads(raw)
            except json.JSONDecodeError:
                return []
        elif isinstance(raw, list):
            items = raw
        else:
            return []
        if not isinstance(items, list):
            return []
        data: list[Any] = []
        for item in items:
            decoded = _item_data(item)
            if decoded is not None:
                data.append(decoded)
        return data

    async def save_all(self, sessions: dict[uuid.UUID, BotSession]) -> None:
        async with self._save_lock, self._pool.acquire() as conn:  # ty: ignore[invalid-context-manager]
            queries = _load_queries("bot_sessions.sql")
            existing_query = "SELECT user_id FROM bot.conversation_sessions"
            existing_rows = await conn.fetch(existing_query)
            existing_ids = {row["user_id"] for row in existing_rows}

            for user_id, bot_session in sessions.items():
                items_json = [to_json_data_item(item) for item in bot_session.data]
                context_dict = {"data": items_json}
                expires_at = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=3650)

                if user_id in existing_ids:
                    await queries.update_conversation_session(  # ty: ignore[unresolved-attribute]
                        conn,
                        user_id=user_id,
                        current_command_code=(
                            int(bot_session.current_command)
                            if bot_session.current_command is not None
                            else None
                        ),
                        last_input_date=bot_session.date,
                        init_state=bool(bot_session._init_state),
                        context=json.dumps(context_dict),
                        expires_at=expires_at,
                    )
                else:
                    await queries.insert_conversation_session(  # ty: ignore[unresolved-attribute]
                        conn,
                        user_id=user_id,
                        current_command_code=(
                            int(bot_session.current_command)
                            if bot_session.current_command is not None
                            else None
                        ),
                        last_input_date=bot_session.date,
                        init_state=bot_session._init_state,
                        context=json.dumps(context_dict),
                        expires_at=expires_at,
                    )


class BotSessionManager:
    def __init__(self, store: dict[uuid.UUID, BotSession] | None = None) -> None:
        self._store: dict[uuid.UUID, BotSession] = store if store is not None else {}

    def get_session(self, user_id: uuid.UUID) -> BotSession:
        session = self._store.get(user_id)
        if session is None:
            session = BotSession()
            self._store[user_id] = session
        return session

    def get_all_sessions(self) -> dict[uuid.UUID, BotSession]:
        return self._store


def _item_data(item: Any) -> Any | None:
    if not isinstance(item, dict):
        return None
    type_name = item.get("Type")
    json_data = item.get("Data")
    if type_name is None or json_data is None:
        return None
    if type_name == TAG_LIST_TRAIN:
        return [json_codecs.train_from_json_or_default(x) for x in _json_array(json_data)]
    if type_name == TAG_LIST_STATION:
        return [json_codecs.station_from_json(x) for x in _json_array(json_data)]
    if type_name == TAG_LIST_SUBSCRIPTION:
        return [
            json_codecs.subscription_details_from_json_or_default(x) for x in _json_array(json_data)
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
    except Exception as exc:
        logger.debug("Skipping invalid session item %s: %s", type_name, exc)
    return None


def _json_object(json_data: Any) -> dict | None:
    if not isinstance(json_data, str):
        return None
    try:
        parsed = json.loads(json_data)
    except json.JSONDecodeError, TypeError:
        return None
    return parsed if isinstance(parsed, dict) else None
