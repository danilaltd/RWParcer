"""Feedback services mirroring ``SendFeedbackService`` / ``SendMessageService`` use cases."""

from __future__ import annotations

from uuid import uuid4

from app.application.errors import KeyNotFoundError, UnauthorizedError
from app.application.services.guards import require_not_banned, require_registered
from app.domain.entities import Message, Notification
from app.domain.protocols import MessageRepository, NotificationRepository, UserRepository
from app.domain.value_objects import MessageInfo


async def send_feedback(
    users: UserRepository,
    messages: MessageRepository,
    notifications: NotificationRepository,
    user_id: str,
    content: str,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    await messages.add_message(
        Message(id=uuid4(), sender_id=user_id, receiver_id="moderator", content=content)
    )
    for moderator in await users.get_moderators():
        await notifications.add_notification(
            Notification(
                id=uuid4(),
                user_id=moderator.id,
                content=f"Новое сообщение от {user_id}:\n{content}",
            )
        )


async def send_message(
    users: UserRepository,
    messages: MessageRepository,
    notifications: NotificationRepository,
    user_id: str,
    target_id: str,
    content: str,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    if not await users.is_user_moderator(user_id):
        raise UnauthorizedError(f"Only moderators can send messages {user_id}")
    if not await users.is_user_registered(target_id):
        # The message text reproduces the (typoed) C# string.
        raise KeyNotFoundError(f"User with ID {user_id} not found")
    await messages.add_message(
        Message(id=uuid4(), sender_id="admin", receiver_id=target_id, content=content)
    )
    await notifications.add_notification(
        Notification(
            id=uuid4(), user_id=target_id, content="Новое сообщение! \n" + content
        )
    )


async def get_messages(
    users: UserRepository, messages: MessageRepository, user_id: str
) -> list[MessageInfo]:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    return [_to_info(m) for m in await messages.get_user_messages(user_id)]


async def get_all_messages(
    users: UserRepository, messages: MessageRepository, user_id: str
) -> list[MessageInfo]:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    if not await users.is_user_moderator(user_id):
        raise UnauthorizedError(f"Only moderators can view all messages {user_id}")
    return [_to_info(m) for m in await messages.get_all_messages()]


def _to_info(message: Message) -> MessageInfo:
    return MessageInfo(
        sender_id=message.sender_id,
        receiver_id=message.receiver_id,
        content=message.content,
        sent_date=message.sent_date,
    )
