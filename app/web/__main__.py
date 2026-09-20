"""FastAPI web server entrypoint for running the web interface alongside the bot."""

from __future__ import annotations

import logging
import os

import uvicorn
from app.application.facade import Facade
from app.config import load_settings
from app.infrastructure.db.repositories import (
    FavoritesPostgresRepository,
    MessagePostgresRepository,
    NotificationPostgresRepository,
    SubscriptionPostgresRepository,
    TransportPostgresRepository,
    UserPostgresRepository,
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

    users = UserPostgresRepository(session_factory)
    transport = TransportPostgresRepository(session_factory)
    subscriptions = SubscriptionPostgresRepository(session_factory, transport, logger)
    favorites = FavoritesPostgresRepository(session_factory, transport, logger)
    notifications = NotificationPostgresRepository(session_factory)
    messages = MessagePostgresRepository(session_factory)

    http = AsyncHttpClientFactory(
        proxy_manager_url=settings.proxy.proxy_manager_url,
        logger=logger,
    )
    rw = RwClient(http, logger)

    facade = Facade(
        users=users,
        transport=transport,
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
