"""FastAPI web server entrypoint for running the web interface alongside the bot."""

from __future__ import annotations

import logging
import os

import uvicorn
from app.application.facade import Facade
from app.config import load_settings
from app.infrastructure.db.repositories import (
    AvailabilitySnapshotPostgresRepository,
    FavoritePostgresRepository,
    MessagePostgresRepository,
    NotificationPostgresRepository,
    RolePostgresRepository,
    ServiceRoutePostgresRepository,
    SubscriptionPostgresRepository,
    UserPostgresRepository,
    UserRolePostgresRepository,
)
from app.infrastructure.db.session import EngineHolder
from app.infrastructure.http_client_factory import AsyncHttpClientFactory
from app.infrastructure.logging import PythonLogger
from app.infrastructure.rw_client import RwClient
from app.web.app import create_web_app


def main() -> None:
    settings = load_settings()
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    logger = PythonLogger("rwparcer-web")
    eng_holder = EngineHolder(settings.database)
    session_factory = eng_holder.session_factory

    role = RolePostgresRepository(session_factory)
    user_role = UserRolePostgresRepository(session_factory, role)
    users = UserPostgresRepository(session_factory, user_role)
    service_route = ServiceRoutePostgresRepository(session_factory)
    snapshot = AvailabilitySnapshotPostgresRepository(session_factory)
    subscriptions = SubscriptionPostgresRepository(session_factory, service_route, snapshot)
    favorites = FavoritePostgresRepository(session_factory, service_route)
    notifications = NotificationPostgresRepository(session_factory)
    messages = MessagePostgresRepository(session_factory)

    http = AsyncHttpClientFactory(
        proxy_manager_url=settings.proxy.proxy_manager_url,
        logger=logger,
    )
    rw = RwClient(http, logger)

    facade = Facade(
        users=users,
        transport=service_route,
        subscriptions=subscriptions,
        favorites=favorites,
        notifications=notifications,
        messages=messages,
        rw=rw,
    )

    app = create_web_app(facade)
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
