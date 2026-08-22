"""Favorites services mirroring the C# ``FavoritesService`` use cases."""

from __future__ import annotations

from uuid import uuid4

from app.application.errors import InvalidOperationError, KeyNotFoundError
from app.application.services.guards import require_not_banned, require_registered
from app.domain.entities import Favorite
from app.domain.protocols import FavoritesRepository, UserRepository
from app.domain.value_objects import Train


async def add_to_favorites(
    users: UserRepository, favorites: FavoritesRepository, user_id: str, train: Train
) -> None:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    if await favorites.favorite_exists(user_id, train):
        raise InvalidOperationError(f"Train {train} already in favorites")
    await favorites.add_favorite(Favorite(id=uuid4(), user_id=user_id, train_info=train))


async def get_favorites(
    users: UserRepository, favorites: FavoritesRepository, user_id: str
) -> list[Train]:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    return [f.train_info for f in await favorites.get_favorites(user_id)]


async def is_in_favorites(
    users: UserRepository, favorites: FavoritesRepository, user_id: str, train: Train
) -> bool:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    return await favorites.favorite_exists(user_id, train)


async def remove_from_favorites(
    users: UserRepository, favorites: FavoritesRepository, user_id: str, train: Train
) -> None:
    # The C# use case performs these checks in a different order than the others.
    await require_not_banned(users, user_id)
    await users.update_activity(user_id)
    await require_registered(users, user_id)
    existing = await favorites.get_favorites(user_id)
    match = next((f for f in existing if f.train_info == train), None)
    if match is None:
        raise KeyNotFoundError(f"{user_id} No such favorite")
    await favorites.remove_favorite(match)
