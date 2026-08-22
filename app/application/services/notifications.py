"""Notification services mirroring the C# ``NotificationService`` use case."""

from __future__ import annotations

from app.domain.protocols import NotificationRepository, UserRepository
from app.domain.value_objects import NotificationItem


async def pop_notifications(
    notifications: NotificationRepository, users: UserRepository
) -> list[NotificationItem]:
    """Pop all notifications, then drop the ones for banned users.

    Matches the C# ``PopNotificationsUseCase``: rows are removed from the
    table even when they are filtered out afterwards.
    """
    items = await notifications.pop_all()
    return [
        NotificationItem(user_id=n.user_id, content=n.content)
        for n in items
        if not await users.is_user_banned(n.user_id)
    ]
