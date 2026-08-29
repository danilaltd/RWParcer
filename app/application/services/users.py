"""User services mirroring the C# ``UserService`` use cases."""

from __future__ import annotations

import datetime

from app.application.errors import KeyNotFoundError, UnauthorizedError
from app.application.services.guards import require_registered
from app.domain.entities import User
from app.domain.protocols import UserRepository
from app.domain.value_objects import UserInfo


async def register_user(users: UserRepository, user_id: str) -> None:
    if await users.is_user_registered(user_id):
        return
    await users.add_user(User(id=user_id))


async def _ensure_access(users: UserRepository, user_id: str, target_id: str) -> None:
    """Registered + not banned + (self or moderator) guard chain.

    Mirrors the C# ``UserService`` checks that run before any DB mutation.
    """
    await require_registered(users, user_id)
    if await users.is_user_banned(user_id):
        raise UnauthorizedError(f"User {user_id} is banned")
    if user_id != target_id and not await users.is_user_moderator(user_id):
        raise UnauthorizedError(
            f"User with ID {user_id} not a moderator (can't get {target_id})"
        )


async def _update_activity(users: UserRepository, user_id: str) -> None:
    """C# ``UpdateActivityAsync`` with the original ``try/finally`` semantics.

    The C# code swallows activity-update errors only when the use case body
    already failed (``catch when (originalException != null)``).
    """
    await users.update_activity(user_id)


async def _finally_update(
    users: UserRepository, user_id: str, original_exception: BaseException | None
) -> None:
    try:
        await _update_activity(users, user_id)
    except Exception:
        if original_exception is None:
            raise


async def get_user_by_id(users: UserRepository, user_id: str, target_id: str) -> UserInfo:
    original_exception: BaseException | None = None
    try:
        await _ensure_access(users, user_id, target_id)
        user = await users.get_user_by_id(target_id)
        if user is None:
            raise KeyNotFoundError(f"User with ID {target_id} not found")
        return _to_user(user)
    except BaseException as exc:
        original_exception = exc
        raise
    finally:
        await _finally_update(users, user_id, original_exception)


async def is_user_moderator(users: UserRepository, user_id: str, target_id: str) -> bool:
    original_exception: BaseException | None = None
    try:
        await _ensure_access(users, user_id, target_id)
        return await users.is_user_moderator(target_id)
    except BaseException as exc:
        original_exception = exc
        raise
    finally:
        await _finally_update(users, user_id, original_exception)


async def is_user_banned(users: UserRepository, user_id: str, target_id: str) -> bool:
    original_exception: BaseException | None = None
    try:
        await _ensure_access(users, user_id, target_id)
        return await users.is_user_banned(target_id)
    except BaseException as exc:
        original_exception = exc
        raise
    finally:
        await _finally_update(users, user_id, original_exception)


async def get_users(
    users: UserRepository, user_id: str, time_span: datetime.timedelta
) -> list[UserInfo]:
    """Return users with activity within ``time_span``; the requester must be a moderator."""
    original_exception: BaseException | None = None
    try:
        await _ensure_access(users, user_id, user_id)
        return [_to_user(user) for user in await users.get_last_users(time_span=time_span)]
    except BaseException as exc:
        original_exception = exc
        raise
    finally:
        await _finally_update(users, user_id, original_exception)


def _to_user(user: User) -> UserInfo:
    return UserInfo(
        id=user.id,
        is_moderator=user.is_moderator,
        max_subscriptions=user.max_subscriptions,
        min_update_interval=user.min_subscriptions_interval,
        is_blocked=user.is_blocked,
        last_activity=user.last_activity,
    )
