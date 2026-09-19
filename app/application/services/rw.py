"""RW (rw.by) services mirroring ``GetStationsUseCase`` / ``GetTrainsUseCase``."""

from __future__ import annotations

import uuid

from app.application.services.guards import require_not_banned, require_registered
from app.domain.protocols import RwRepository, UserRepository
from app.domain.value_objects import Route, Station, Train


async def get_stations(
    users: UserRepository, rw: RwRepository, user_id: uuid.UUID, prefix: str
) -> list[Station]:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    return await rw.get_stations(prefix)


async def get_trains_for_route(
    users: UserRepository, rw: RwRepository, user_id: uuid.UUID, route: Route
) -> list[Train]:
    await require_registered(users, user_id)
    await users.update_activity(user_id)
    await require_not_banned(users, user_id)
    return await rw.get_trains(route)
