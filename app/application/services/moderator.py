"""Moderator services mirroring the C# ``ModeratorUseCases``."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.services.guards import (
    require_moderator,
    require_not_banned,
    require_registered,
)

if TYPE_CHECKING:
    import uuid

    from app.domain.protocols import UserRepository


async def ban_user(users: UserRepository, user_id: uuid.UUID, target_id: uuid.UUID) -> None:
    await _require_actor(users, user_id, "ban")
    await users.ban_user(target_id)


async def unban_user(users: UserRepository, user_id: uuid.UUID, target_id: uuid.UUID) -> None:
    await _require_actor(users, user_id, "unban")
    await users.unban_user(target_id)


async def promote_user(users: UserRepository, user_id: uuid.UUID, target_id: uuid.UUID) -> None:
    await _require_actor(users, user_id, "promote")
    await users.promote_user(target_id)


async def demote_user(users: UserRepository, user_id: uuid.UUID, target_id: uuid.UUID) -> None:
    await _require_actor(users, user_id, "demote")
    await users.demote_user(target_id)


async def set_users_max_subscriptions(
    users: UserRepository, user_id: uuid.UUID, target_id: uuid.UUID, max_subscriptions: int
) -> None:
    await _require_actor(users, user_id, "set max subscriptions")
    await users.set_users_max_subscriptions(target_id, max_subscriptions)


async def set_users_min_subscriptions_interval(
    users: UserRepository, user_id: uuid.UUID, target_id: uuid.UUID, min_interval: int
) -> None:
    await _require_actor(users, user_id, "set interval")
    await users.set_users_min_interval(target_id, min_interval)


async def _require_actor(users: UserRepository, user_id: uuid.UUID, action: str) -> None:
    """Shared guard: actor is registered, active and a moderator."""
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    await require_moderator(users, user_id, action)
