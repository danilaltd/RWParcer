"""Notification services using outbox queue."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from app.domain.value_objects import NotificationItem

if TYPE_CHECKING:
    from app.domain.protocols import NotificationRepository, UserRepository

UTC = datetime.UTC


async def pop_notifications(
    notifications: NotificationRepository, users: UserRepository
) -> list[NotificationItem]:
    items = await notifications.claim_pending_notifications(limit=50)
    results = []
    for n in items:
        if await users.is_user_banned(n.user_id):
            await notifications.mark_failed(n.id, "User is banned")
            continue
        results.append(NotificationItem(user_id=str(n.user_id), content=n.content))
        await notifications.mark_sent(n.id)
    return results
