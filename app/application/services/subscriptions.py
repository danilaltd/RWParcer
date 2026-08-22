"""Subscription services mirroring the C# ``SubscriptionService`` use cases."""

from __future__ import annotations

from uuid import uuid4

from app.application.errors import InvalidOperationError, KeyNotFoundError, UnauthorizedError
from app.application.services.guards import require_not_banned, require_registered
from app.domain.entities import Subscription
from app.domain.protocols import SubscriptionRepository, UserRepository
from app.domain.value_objects import SubscriptionDetails


async def subscribe(
    users: UserRepository,
    subs: SubscriptionRepository,
    user_id: str,
    subscription: SubscriptionDetails,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    if await subs.subscription_exists(user_id, subscription):
        raise InvalidOperationError(f"{user_id} already has this subscription")
    count = await subs.get_subscription_count(user_id)
    user = await users.get_user_by_id(user_id)
    if user is None:
        raise KeyNotFoundError(f"User with ID {user_id} not found")
    if count >= user.max_subscriptions:
        raise OverflowError(
            f"User {user_id} reached the subscription limit ({user.max_subscriptions})"
        )
    await subs.add_subscription(
        Subscription(id=uuid4(), user_id=user_id, details=subscription)
    )


async def unsubscribe(
    users: UserRepository,
    subs: SubscriptionRepository,
    user_id: str,
    subscription: SubscriptionDetails,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    existing = await subs.get_user_subscriptions(user_id)
    match = next((s for s in existing if s.details == subscription), None)
    if match is None:
        raise InvalidOperationError(f"{user_id} No such subscription")
    await subs.remove_subscription(match)


async def reset_subscribe(
    users: UserRepository,
    subs: SubscriptionRepository,
    user_id: str,
    subscription: SubscriptionDetails,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    existing = await subs.get_user_subscriptions(user_id)
    match = next((s for s in existing if s.details == subscription), None)
    if match is None:
        raise InvalidOperationError(f"{user_id} No such subscription")
    await subs.reset_subscription(match)


async def get_subscriptions(
    users: UserRepository, subs: SubscriptionRepository, user_id: str, target_id: str
) -> list[SubscriptionDetails]:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    if user_id != target_id and not await users.is_user_moderator(user_id):
        raise UnauthorizedError(
            f"{user_id} tries get {target_id} subscriptions when not moder"
        )
    return [s.details for s in await subs.get_user_subscriptions(target_id)]
