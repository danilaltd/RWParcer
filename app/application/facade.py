"""Application facade wiring normalized repositories and services."""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING, Any

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
from app.domain import json_codecs
from app.domain.entities import User
from app.domain.value_objects import (
    MessageInfo,
    NotificationItem,
    Route,
    Station,
    SubscriptionDetails,
    Train,
    UserInfo,
)

if TYPE_CHECKING:
    import datetime

    from app.domain.protocols import (
        FavoritesRepository,
        MessageRepository,
        NotificationRepository,
        RwRepository,
        SubscriptionRepository,
        TransportRepository,
        UserRepository,
    )


class DummyTransport:
    async def get_or_create_service_route(self, details: SubscriptionDetails) -> uuid.UUID:
        return uuid.uuid4()


class Facade:
    def __init__(
        self,
        users: UserRepository,
        transport: TransportRepository,
        subscriptions: SubscriptionRepository,
        favorites: FavoritesRepository,
        notifications: NotificationRepository,
        messages: MessageRepository,
        rw: RwRepository,
    ) -> None:
        self._users = users
        self._transport = transport
        self._subscriptions = subscriptions
        self._favorites = favorites
        self._notifications = notifications
        self._messages = messages
        self._rw = rw

    @property
    def users_repo(self) -> UserRepository:
        return self._users

    async def authenticate_user(
        self, telegram_user_id: int | str | uuid.UUID, telegram_chat_id: int | str | None = None
    ) -> uuid.UUID:
        if isinstance(telegram_user_id, uuid.UUID):
            return telegram_user_id
        if isinstance(telegram_user_id, str):
            try:
                return uuid.UUID(telegram_user_id)
            except ValueError:
                try:
                    uid_int = int(telegram_user_id)
                    chat_int = int(telegram_chat_id) if telegram_chat_id is not None else uid_int
                    user = await users_service.resolve_user(self._users, uid_int, chat_int)
                    return user.id
                except Exception:
                    u_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, telegram_user_id)
                    if not await self._users.is_user_registered(u_uuid):
                        await self._users.add_user(
                            User(id=u_uuid, telegram_user_id=0, telegram_chat_id=0)
                        )
                    return u_uuid
        chat_id = telegram_chat_id if telegram_chat_id is not None else telegram_user_id
        user = await users_service.resolve_user(self._users, int(telegram_user_id), int(chat_id))
        return user.id

    async def get_station(self, user_id: uuid.UUID | str, prefix: str) -> list[Station]:
        uid = await self.authenticate_user(user_id)
        return await rw_service.get_stations(self._users, self._rw, uid, prefix)

    async def get_times_for_route(self, user_id: uuid.UUID | str, route: Route) -> list[Train]:
        uid = await self.authenticate_user(user_id)
        return await rw_service.get_trains_for_route(self._users, self._rw, uid, route)

    async def add_to_favorites(self, user_id: uuid.UUID | str, train: Train) -> None:
        uid = await self.authenticate_user(user_id)
        await favorites_service.add_to_favorites(
            self._users, self._transport, self._favorites, uid, train
        )

    async def is_in_favorites(self, user_id: uuid.UUID | str, train: Train) -> bool:
        uid = await self.authenticate_user(user_id)
        return await favorites_service.is_in_favorites(
            self._users, self._transport, self._favorites, uid, train
        )

    async def remove_from_favorites(self, user_id: uuid.UUID | str, train: Train) -> None:
        uid = await self.authenticate_user(user_id)
        await favorites_service.remove_from_favorites(self._users, self._favorites, uid, train)

    async def get_favorites(self, user_id: uuid.UUID | str) -> list[Train]:
        uid = await self.authenticate_user(user_id)
        return await favorites_service.get_favorites(self._users, self._favorites, uid)

    async def subscribe(self, user_id: uuid.UUID | str, subscription: SubscriptionDetails) -> None:
        uid = await self.authenticate_user(user_id)
        await subscriptions_service.subscribe(
            self._users, self._transport, self._subscriptions, uid, subscription
        )

    async def unsubscribe(
        self, user_id: uuid.UUID | str, subscription: SubscriptionDetails
    ) -> None:
        uid = await self.authenticate_user(user_id)
        await subscriptions_service.unsubscribe(self._users, self._subscriptions, uid, subscription)

    async def reset_subscription(
        self, user_id: uuid.UUID | str, subscription: SubscriptionDetails
    ) -> None:
        uid = await self.authenticate_user(user_id)
        await subscriptions_service.reset_subscribe(
            self._users, self._subscriptions, uid, subscription
        )

    async def get_subscriptions(
        self, user_id: uuid.UUID | str, target_id: uuid.UUID | str
    ) -> list[SubscriptionDetails]:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        return await subscriptions_service.get_subscriptions(
            self._users, self._subscriptions, uid, tid
        )

    async def pop_notifications(self) -> list[NotificationItem]:
        return await notifications_service.pop_notifications(self._notifications, self._users)

    async def ban_user(self, user_id: uuid.UUID | str, target_id: uuid.UUID | str) -> None:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        await moderator_service.ban_user(self._users, uid, tid)

    async def unban_user(self, user_id: uuid.UUID | str, target_id: uuid.UUID | str) -> None:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        await moderator_service.unban_user(self._users, uid, tid)

    async def promote_user(self, user_id: uuid.UUID | str, target_id: uuid.UUID | str) -> None:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        await moderator_service.promote_user(self._users, uid, tid)

    async def demote_user(self, user_id: uuid.UUID | str, target_id: uuid.UUID | str) -> None:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        await moderator_service.demote_user(self._users, uid, tid)

    async def set_users_max_subscriptions(
        self, user_id: uuid.UUID | str, target_id: uuid.UUID | str, max_subscriptions: int
    ) -> None:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        await moderator_service.set_users_max_subscriptions(
            self._users, uid, tid, max_subscriptions
        )

    async def set_users_min_interval(
        self, user_id: uuid.UUID | str, target_id: uuid.UUID | str, min_interval: int
    ) -> None:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        await moderator_service.set_users_min_subscriptions_interval(
            self._users, uid, tid, min_interval
        )

    async def get_users(
        self, user_id: uuid.UUID | str, time_span: datetime.timedelta
    ) -> list[UserInfo]:
        uid = await self.authenticate_user(user_id)
        return await users_service.get_users(self._users, uid, time_span)

    async def is_user_moderator(self, user_id: uuid.UUID | str, target_id: uuid.UUID | str) -> bool:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        return await users_service.is_user_moderator(self._users, uid, tid)

    async def is_user_banned(self, user_id: uuid.UUID | str, target_id: uuid.UUID | str) -> bool:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        return await users_service.is_user_banned(self._users, uid, tid)

    async def get_user_by_id(
        self, user_id: uuid.UUID | str, target_id: uuid.UUID | str
    ) -> UserInfo:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        return await users_service.get_user_by_id(self._users, uid, tid)

    async def send_feedback(self, user_id: uuid.UUID | str, content: str) -> None:
        uid = await self.authenticate_user(user_id)
        await feedback_service.send_feedback(
            self._users, self._messages, self._notifications, uid, content
        )

    async def send_message(
        self, user_id: uuid.UUID | str, target_id: uuid.UUID | str, content: str
    ) -> None:
        uid = await self.authenticate_user(user_id)
        tid = await self.authenticate_user(target_id)
        await feedback_service.send_message(
            self._users, self._messages, self._notifications, uid, tid, content
        )

    async def get_messages(self, user_id: uuid.UUID | str) -> list[MessageInfo]:
        uid = await self.authenticate_user(user_id)
        return await feedback_service.get_messages(self._users, self._messages, uid)

    async def get_all_messages(self, user_id: uuid.UUID | str) -> list[MessageInfo]:
        uid = await self.authenticate_user(user_id)
        return await feedback_service.get_all_messages(self._users, self._messages, uid)

    def serialize_to_json(self, obj: Any) -> str:
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
