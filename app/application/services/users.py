"""User services using UUID user identifiers and normalized schema repositories."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from app.application.services.guards import (
    require_moderator,
    require_not_banned,
    require_registered,
)
from app.domain.value_objects import UserInfo

if TYPE_CHECKING:
    import uuid

    from app.domain.entities import User
    from app.domain.protocols import UserRepository


async def authenticate_user(
    users: UserRepository,
    telegram_user_id: int,
    telegram_chat_id: int,
) -> User:
    # TODO: divide register_user and authenticate_user
    return await users.register_user(telegram_user_id, telegram_chat_id, "", "")


async def register_user(
    users: UserRepository,
    telegram_user_id: int,
    telegram_chat_id: int,
    username: str | None,
    display_name: str,
) -> User:
    # if await users.is_user_registered(user_id):
    # raise ValueError(f"User with ID {user_id} is already registered")
    return await users.register_user(telegram_user_id, telegram_chat_id, username, display_name)
    # await users.add_user(User(id=user_id, telegram_user_id=0, telegram_chat_id=0))


async def _ensure_access(
    users: UserRepository, user_id: uuid.UUID, target_id: uuid.UUID, action: str
) -> None:
    await require_registered(users, user_id)
    await require_not_banned(users, user_id)
    if user_id != target_id:
        await require_moderator(users, user_id, action)


async def _update_activity(users: UserRepository, user_id: uuid.UUID) -> None:
    await users.update_activity(user_id)


async def _finally_update(
    users: UserRepository, user_id: uuid.UUID, original_exception: BaseException | None
) -> None:
    try:
        await _update_activity(users, user_id)
    except Exception:
        if original_exception is None:
            raise


async def get_user_by_id(
    users: UserRepository, user_id: uuid.UUID, target_id: uuid.UUID
) -> UserInfo:
    original_exception: BaseException | None = None
    try:
        await _ensure_access(users, user_id, target_id, "get user info")
        user = await users.get_user_by_id(target_id)
        if user is None:
            raise KeyError(f"User with ID {target_id} not found")
        return _to_user(user)
    except BaseException as exc:
        original_exception = exc
        raise
    finally:
        await _finally_update(users, user_id, original_exception)


async def is_user_moderator(
    users: UserRepository, user_id: uuid.UUID, target_id: uuid.UUID
) -> bool:
    original_exception: BaseException | None = None
    try:
        await _ensure_access(users, user_id, target_id, "check moderator status")
        return await users.is_user_moderator(target_id)
    except BaseException as exc:
        original_exception = exc
        raise
    finally:
        await _finally_update(users, user_id, original_exception)


async def is_user_banned(users: UserRepository, user_id: uuid.UUID, target_id: uuid.UUID) -> bool:
    original_exception: BaseException | None = None
    try:
        await _ensure_access(users, user_id, target_id, "check ban status")
        return await users.is_user_banned(target_id)
    except BaseException as exc:
        original_exception = exc
        raise
    finally:
        await _finally_update(users, user_id, original_exception)


async def get_users(
    users: UserRepository, user_id: uuid.UUID, time_span: datetime.timedelta
) -> list[UserInfo]:
    original_exception: BaseException | None = None
    try:
        await _ensure_access(users, user_id, user_id, "view users")
        return [_to_user(user) for user in await users.get_last_users(time_span=time_span)]
    except BaseException as exc:
        original_exception = exc
        raise
    finally:
        await _finally_update(users, user_id, original_exception)


def _to_user(user: User) -> UserInfo:
    return UserInfo(
        id=user.id,
        telegram_user_id=user.telegram_user_id,
        username=user.username,
        display_name=user.display_name,
        is_moderator=user.is_moderator,
        max_subscriptions=user.max_subscriptions,
        min_update_interval=user.min_subscriptions_interval,
        is_blocked=user.is_blocked,
        last_activity=user.last_activity or datetime.datetime.now(datetime.UTC),
    )
