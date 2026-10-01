"""Shared guard helpers replicating the checks common to every use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import uuid

    from app.domain.protocols import UserRepository


async def require_registered(users: UserRepository, user_id: uuid.UUID) -> None:
    if not await users.is_user_registered(user_id):
        raise KeyError(f"User with ID {user_id} not found")


async def require_not_banned(users: UserRepository, user_id: uuid.UUID) -> None:
    if await users.is_user_banned(user_id):
        raise PermissionError(f"User {user_id} is banned")


async def require_moderator(users: UserRepository, user_id: uuid.UUID, action: str) -> None:
    if not await users.is_user_moderator(user_id):
        raise PermissionError(f"Only moderators can {action} users {user_id}")
