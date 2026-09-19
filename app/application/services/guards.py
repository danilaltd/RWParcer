"""Shared guard helpers replicating the checks common to every use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.errors import KeyNotFoundError, UnauthorizedError

if TYPE_CHECKING:
    import uuid

    from app.domain.protocols import UserRepository


async def require_registered(users: UserRepository, user_id: uuid.UUID) -> None:
    if not await users.is_user_registered(user_id):
        raise KeyNotFoundError(f"User with ID {user_id} not found")


async def require_not_banned(users: UserRepository, user_id: uuid.UUID) -> None:
    if await users.is_user_banned(user_id):
        raise UnauthorizedError(f"User {user_id} is banned")
