"""Subscription services integrating with normalized

transport service routes and user repositories.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from app.application.services.guards import (
    require_moderator,
    require_not_banned,
    require_registered,
)
from app.domain.entities import Subscription

if TYPE_CHECKING:
    from app.domain.protocols import ServiceRouteRepository, SubscriptionRepository, UserRepository
    from app.domain.value_objects import SubscriptionDetails


async def subscribe(
    users: UserRepository,
    transport: ServiceRouteRepository,
    subs: SubscriptionRepository,
    user_id: uuid.UUID,
    subscription: SubscriptionDetails,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)

    service_route_id = await transport.get_or_create_service_route(subscription)
    if await subs.subscription_exists(user_id, service_route_id, subscription.date):
        raise RuntimeError(f"{user_id} already has this subscription")

    count = await subs.get_subscription_count(user_id)
    user = await users.get_user_by_id(user_id)
    if user is None:
        raise KeyError(f"User with ID {user_id} not found")
    if count >= user.max_subscriptions:
        raise OverflowError(
            f"User {user_id} reached the subscription limit ({user.max_subscriptions})"
        )

    await subs.add_subscription(
        Subscription(
            id=uuid.uuid4(),
            user_id=user_id,
            service_route_id=service_route_id,
            target_date=subscription.date,
            details=subscription,
        )
    )


async def unsubscribe(
    users: UserRepository,
    subs: SubscriptionRepository,
    user_id: uuid.UUID,
    subscription: SubscriptionDetails,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    existing = await subs.get_user_subscriptions(user_id)
    match = next((s for s in existing if s.details == subscription), None)
    if match is None:
        raise RuntimeError(f"{user_id} No such subscription")
    await subs.remove_subscription(match)


async def reset_subscribe(
    users: UserRepository,
    subs: SubscriptionRepository,
    user_id: uuid.UUID,
    subscription: SubscriptionDetails,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    existing = await subs.get_user_subscriptions(user_id)
    match = next((s for s in existing if s.details == subscription), None)
    if match is None:
        raise RuntimeError(f"{user_id} No such subscription")
    await subs.reset_subscription(match)


async def get_subscriptions(
    users: UserRepository, subs: SubscriptionRepository, user_id: uuid.UUID, target_id: uuid.UUID
) -> list[SubscriptionDetails]:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    if user_id != target_id:
        await require_moderator(users, user_id, "get subscriptions for other users")
    return [s.details for s in await subs.get_user_subscriptions(target_id)]
