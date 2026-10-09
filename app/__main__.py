"""Composition root — the Python twin of ``RWParcer/Program.cs``.

Runs the bot with ``python -m app``. Wires repositories, rw.by client,
facade, router and ``BotService`` from :func:`app.config.load_settings`.
"""

from __future__ import annotations

import asyncio
import logging
import os
import signal

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties

from app.application.facade import Facade
from app.application.notifier import Notifier
from app.bot.router import CommandRouter
from app.bot.service import BotService
from app.bot.storage import SessionStorage
from app.config import Settings, load_settings
from app.infrastructure.db.pool import ConnectionPool
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
from app.infrastructure.http_client_factory import AsyncHttpClientFactory
from app.infrastructure.logging import PythonLogger
from app.infrastructure.rw_client import RwClient


async def _build(settings: Settings) -> tuple[BotService, Bot, ConnectionPool]:
    logger = PythonLogger("rwparcer")
    connection_pool = await ConnectionPool.create(settings.database)

    role = RolePostgresRepository(connection_pool)
    user_role = UserRolePostgresRepository(connection_pool, role)
    users = UserPostgresRepository(connection_pool, user_role)
    service_route = ServiceRoutePostgresRepository(connection_pool)
    snapshot = AvailabilitySnapshotPostgresRepository(connection_pool)
    subscriptions = SubscriptionPostgresRepository(connection_pool, service_route, snapshot)
    favorites = FavoritePostgresRepository(connection_pool, service_route)
    notifications = NotificationPostgresRepository(connection_pool)
    messages = MessagePostgresRepository(connection_pool)

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
    notifier = Notifier(subscriptions, notifications, users, rw, logger)
    asyncio.create_task(notifier.run(asyncio.Event()))
    bot = Bot(token=settings.bot.token, default=DefaultBotProperties(parse_mode="HTML"))
    router = CommandRouter(facade)
    store = SessionStorage(connection_pool)

    service = BotService(
        bot=bot,
        store=store,
        facade=facade,
        router=router,
        allowed_updates=settings.bot.allowed_updates,
        poll_interval=settings.notifier.poll_interval,
    )
    return service, bot, connection_pool


async def _amain() -> None:
    settings = load_settings()
    if not settings.bot.token:
        raise SystemExit("BOT_TOKEN is not configured")

    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "DEBUG").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("httpx").setLevel(logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.INFO)

    service, bot, connection_pool = await _build(settings)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(service.stop()))

    try:
        await service.start()
        logging.getLogger("rwparcer").info("Bot started")
        await service.wait()
    except KeyboardInterrupt, SystemExit:
        pass
    finally:
        await service.stop()
        if bot.session is not None:
            await bot.session.close()
        await connection_pool.close()


def main() -> None:
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
