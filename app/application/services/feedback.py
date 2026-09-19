"""Feedback and message services using UUID user identifiers."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.application.errors import KeyNotFoundError, UnauthorizedError
from app.application.services.guards import require_not_banned, require_registered
from app.domain.entities import Message, Notification
from app.domain.value_objects import MessageInfo

if TYPE_CHECKING:
    from app.domain.protocols import MessageRepository, NotificationRepository, UserRepository


async def send_feedback(
    users: UserRepository,
    messages: MessageRepository,
    notifications: NotificationRepository,
    user_id: uuid.UUID,
    content: str,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    await messages.add_message(
        Message(id=uuid.uuid4(), sender_id=user_id, receiver_id=None, content=content)
    )
    for moderator in await users.get_moderators():
        await notifications.add_notification(
            Notification(
                id=uuid.uuid4(),
                user_id=moderator.id,
                content=f"Новое сообщение от {user_id}:\n{content}",
            )
        )


async def send_message(
    users: UserRepository,
    messages: MessageRepository,
    notifications: NotificationRepository,
    user_id: uuid.UUID,
    target_id: uuid.UUID,
    content: str,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    if not await users.is_user_moderator(user_id):
        raise UnauthorizedError(f"Only moderators can send messages {user_id}")
    if not await users.is_user_registered(target_id):
        raise KeyNotFoundError(f"User with ID {target_id} not found")
    await messages.add_message(
        Message(id=uuid.uuid4(), sender_id=user_id, receiver_id=target_id, content=content)
    )
    await notifications.add_notification(
        Notification(id=uuid.uuid4(), user_id=target_id, content="Новое сообщение! \n" + content)
    )


async def get_messages(
    users: UserRepository, messages: MessageRepository, user_id: uuid.UUID
) -> list[MessageInfo]:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    return [_to_info(m) for m in await messages.get_user_messages(user_id)]


async def get_all_messages(
    users: UserRepository, messages: MessageRepository, user_id: uuid.UUID
) -> list[MessageInfo]:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    if not await users.is_user_moderator(user_id):
        raise UnauthorizedError(f"Only moderators can view all messages {user_id}")
    return [_to_info(m) for m in await messages.get_all_messages()]


def _to_info(message: Message) -> MessageInfo:
    return MessageInfo(
        sender_id=str(message.sender_id) if message.sender_id else "",
        receiver_id=str(message.receiver_id) if message.receiver_id else "",
        content=message.content,
        sent_date=message.sent_date,
    )
