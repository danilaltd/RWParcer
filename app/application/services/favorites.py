"""Favorites services using normalized schema."""

from __future__ import annotations

import datetime
import uuid
from typing import TYPE_CHECKING

from app.application.errors import InvalidOperationError, KeyNotFoundError
from app.application.services.guards import require_not_banned, require_registered
from app.domain.entities import Favorite
from app.domain.value_objects import SubscriptionDetails, Train

if TYPE_CHECKING:
    from app.domain.protocols import FavoritesRepository, TransportRepository, UserRepository


async def add_to_favorites(
    users: UserRepository,
    transport: TransportRepository,
    favorites: FavoritesRepository,
    user_id: uuid.UUID,
    train: Train,
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    service_route_id = await transport.get_or_create_service_route(
        SubscriptionDetails(train=train, date=datetime.date.today())
    )
    if await favorites.favorite_exists(user_id, service_route_id):
        raise InvalidOperationError(f"Train {train} already in favorites")
    await favorites.add_favorite(
        Favorite(
            id=uuid.uuid4(), user_id=user_id, service_route_id=service_route_id, train_info=train
        )
    )


async def get_favorites(
    users: UserRepository, favorites: FavoritesRepository, user_id: uuid.UUID
) -> list[Train]:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    items = await favorites.get_favorites(user_id)
    return [f.train_info for f in items]


async def is_in_favorites(
    users: UserRepository,
    transport: TransportRepository,
    favorites: FavoritesRepository,
    user_id: uuid.UUID,
    train: Train,
) -> bool:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    service_route_id = await transport.get_or_create_service_route(
        SubscriptionDetails(train=train, date=datetime.date.today())
    )
    return await favorites.favorite_exists(user_id, service_route_id)


async def remove_from_favorites(
    users: UserRepository, favorites: FavoritesRepository, user_id: uuid.UUID, train: Train
) -> None:
    await require_not_banned(users, user_id)
    await users.update_activity(user_id)
    await require_registered(users, user_id)
    existing = await favorites.get_favorites(user_id)
    match = next((f for f in existing if f.train_info == train), None)
    if match is None:
        raise KeyNotFoundError(f"{user_id} No such favorite")
    await favorites.remove_favorite(match)
