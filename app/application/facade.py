"""Application facade — the single entry point for the bot and notifier.

Mirrors ``IFacade``/``Facade`` from the C# project. The facade owns the
repositories, the rw.by client and the background notifier; the composition
root wires it together.
"""

from __future__ import annotations

import datetime
import json
from typing import Any

from app.application.services import (
    favorites as favorites_service,
)
from app.application.services import (
    feedback as feedback_service,
)
from app.application.services import (
    moderator as moderator_service,
)
from app.application.services import (
    notifications as notifications_service,
)
from app.application.services import (
    rw as rw_service,
)
from app.application.services import (
    subscriptions as subscriptions_service,
)
from app.application.services import (
    users as users_service,
)

# from app.application.notifier import Notifier (imported lazily to avoid cycles)
from app.domain import json_codecs
from app.domain.protocols import (
    FavoritesRepository,
    MessageRepository,
    NotificationRepository,
    RwRepository,
    SubscriptionRepository,
    UserRepository,
)
from app.domain.value_objects import (
    MessageInfo,
    NotificationItem,
    Route,
    Station,
    SubscriptionDetails,
    Train,
    UserInfo,
)


class Facade:
    def __init__(
        self,
        users: UserRepository,
        subscriptions: SubscriptionRepository,
        favorites: FavoritesRepository,
        notifications: NotificationRepository,
        messages: MessageRepository,
        rw: RwRepository,
    ) -> None:
        self._users = users
        self._subscriptions = subscriptions
        self._favorites = favorites
        self._notifications = notifications
        self._messages = messages
        self._rw = rw

    # -- auth ----------------------------------------------------------------
    async def authenticate_user(self, user_id: str) -> None:
        await users_service.register_user(self._users, user_id)

    # -- rw.by lookups -------------------------------------------------------
    async def get_station(self, user_id: str, prefix: str) -> list[Station]:
        return await rw_service.get_stations(self._users, self._rw, user_id, prefix)

    async def get_times_for_route(self, user_id: str, route: Route) -> list[Train]:
        return await rw_service.get_trains_for_route(self._users, self._rw, user_id, route)

    # -- favorites -----------------------------------------------------------
    async def add_to_favorites(self, user_id: str, train: Train) -> None:
        await favorites_service.add_to_favorites(self._users, self._favorites, user_id, train)

    async def is_in_favorites(self, user_id: str, train: Train) -> bool:
        return await favorites_service.is_in_favorites(self._users, self._favorites, user_id, train)

    async def remove_from_favorites(self, user_id: str, train: Train) -> None:
        await favorites_service.remove_from_favorites(self._users, self._favorites, user_id, train)

    async def get_favorites(self, user_id: str) -> list[Train]:
        return await favorites_service.get_favorites(self._users, self._favorites, user_id)

    # -- subscriptions -------------------------------------------------------
    async def subscribe(self, user_id: str, subscription: SubscriptionDetails) -> None:
        await subscriptions_service.subscribe(
            self._users, self._subscriptions, user_id, subscription
        )

    async def unsubscribe(self, user_id: str, subscription: SubscriptionDetails) -> None:
        await subscriptions_service.unsubscribe(
            self._users, self._subscriptions, user_id, subscription
        )

    async def reset_subscription(self, user_id: str, subscription: SubscriptionDetails) -> None:
        await subscriptions_service.reset_subscribe(
            self._users, self._subscriptions, user_id, subscription
        )

    async def get_subscriptions(self, user_id: str, target_id: str) -> list[SubscriptionDetails]:
        return await subscriptions_service.get_subscriptions(
            self._users, self._subscriptions, user_id, target_id
        )

    # -- notifications -------------------------------------------------------
    async def pop_notifications(self) -> list[NotificationItem]:
        return await notifications_service.pop_notifications(self._notifications, self._users)

    # -- moderation ----------------------------------------------------------
    async def ban_user(self, user_id: str, target_id: str) -> None:
        await moderator_service.ban_user(self._users, user_id, target_id)

    async def unban_user(self, user_id: str, target_id: str) -> None:
        await moderator_service.unban_user(self._users, user_id, target_id)

    async def promote_user(self, user_id: str, target_id: str) -> None:
        await moderator_service.promote_user(self._users, user_id, target_id)

    async def demote_user(self, user_id: str, target_id: str) -> None:
        await moderator_service.demote_user(self._users, user_id, target_id)

    async def set_users_max_subscriptions(
        self, user_id: str, target_id: str, max_subscriptions: int
    ) -> None:
        await moderator_service.set_users_max_subscriptions(
            self._users, user_id, target_id, max_subscriptions
        )

    async def set_users_min_interval(self, user_id: str, target_id: str, min_interval: int) -> None:
        await moderator_service.set_users_min_subscriptions_interval(
            self._users, user_id, target_id, min_interval
        )

    async def get_users(self, user_id: str, time_span: datetime.timedelta) -> list[UserInfo]:
        return await users_service.get_users(self._users, user_id, time_span)

    async def is_user_moderator(self, user_id: str, target_id: str) -> bool:
        return await users_service.is_user_moderator(self._users, user_id, target_id)

    async def is_user_banned(self, user_id: str, target_id: str) -> bool:
        return await users_service.is_user_banned(self._users, user_id, target_id)

    async def get_user_by_id(self, user_id: str, target_id: str) -> UserInfo:
        return await users_service.get_user_by_id(self._users, user_id, target_id)

    # -- feedback / messages -------------------------------------------------
    async def send_feedback(self, user_id: str, content: str) -> None:
        await feedback_service.send_feedback(
            self._users, self._messages, self._notifications, user_id, content
        )

    async def send_message(self, user_id: str, target_id: str, content: str) -> None:
        await feedback_service.send_message(
            self._users, self._messages, self._notifications, user_id, target_id, content
        )

    async def get_messages(self, user_id: str) -> list[MessageInfo]:
        return await feedback_service.get_messages(self._users, self._messages, user_id)

    async def get_all_messages(self, user_id: str) -> list[MessageInfo]:
        return await feedback_service.get_all_messages(self._users, self._messages, user_id)

    # -- raw JSON helpers (parity with ``IFacade``/``JsonOperationsUseCase``) -
    def serialize_to_json(self, obj: Any) -> str:
        """Serialize a known value object to a JSON string (``SerializeToJson``)."""
        data: Any
        if isinstance(obj, Train):
            data = json_codecs.train_to_json(obj)
        elif isinstance(obj, SubscriptionDetails):
            data = json_codecs.subscription_details_to_json(obj)
        elif isinstance(obj, Station):
            data = json_codecs.station_to_json(obj)
        elif isinstance(obj, Route):
            data = json_codecs.route_to_json(obj)
        elif isinstance(obj, UserInfo):
            data = json_codecs.user_to_json(obj)
        elif isinstance(obj, MessageInfo):
            data = json_codecs.message_to_json(obj)
        else:
            data = obj
        return json.dumps(data, ensure_ascii=False, sort_keys=False)

    def deserialize_from_json(self, json_str: str, target: type) -> Any:
        """Deserialize a JSON string into ``target`` (``DeserializeFromJson<T>``)."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return None
        if target is Train:
            return json_codecs.train_from_json_or_default(data)
        if target is SubscriptionDetails:
            return json_codecs.subscription_details_from_json_or_default(data)
        if target is Station:
            return json_codecs.station_from_json(data)
        if target is Route:
            return json_codecs.route_from_json(data)
        if target is UserInfo:
            return json_codecs.user_from_json(data)
        if target is MessageInfo:
            return json_codecs.message_from_json(data)
        return data
