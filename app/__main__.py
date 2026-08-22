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

from app.application.facade import Facade
from app.bot.router import CommandRouter
from app.bot.service import BotService
from app.bot.storage import SessionStorage
from app.config import load_settings
from app.infrastructure.db.repositories import (
    FavoritesPostgresRepository,
    MessagePostgresRepository,
    NotificationPostgresRepository,
    SubscriptionPostgresRepository,
    UserPostgresRepository,
)
from app.infrastructure.db.session import EngineHolder
from app.infrastructure.http_client_factory import AsyncHttpClientFactory
from app.infrastructure.logging import PythonLogger
from app.infrastructure.rw_client import RwClient


def _build(settings) -> tuple[BotService, Bot, EngineHolder]:
    logger = PythonLogger("rwparcer")
    engine_holder = EngineHolder(settings.database)
    session_factory = engine_holder.session_factory

    users = UserPostgresRepository(session_factory)
    subscriptions = SubscriptionPostgresRepository(session_factory, logger)
    favorites = FavoritesPostgresRepository(session_factory, logger)
    notifications = NotificationPostgresRepository(session_factory)
    messages = MessagePostgresRepository(session_factory)

    http = AsyncHttpClientFactory(
        proxy_manager_url=settings.proxy.proxy_manager_url,
        logger=logger,
    )
    rw = RwClient(http, logger)

    facade = Facade(users, subscriptions, favorites, notifications, messages, rw)

    bot = Bot(token=settings.bot.token)
    router = CommandRouter(facade)
    store = SessionStorage(session_factory)

    service = BotService(
        bot=bot,
        store=store,
        facade=facade,
        router=router,
        allowed_updates=settings.bot.allowed_updates,
        poll_interval=settings.notifier.poll_interval,
    )
    return service, bot, engine_holder


async def _amain() -> None:
    settings = load_settings()
    if not settings.bot.token:
        raise SystemExit("BOT_TOKEN is not configured")

    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    service, bot, engine_holder = _build(settings)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda: asyncio.create_task(service.stop())
        )

    try:
        await service.start()
        logging.getLogger("rwparcer").info("Bot started")
        await service.wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        await service.stop()
        if bot.session is not None:
            await bot.session.close()
        await engine_holder.dispose()


def main() -> None:
    asyncio.run(_amain())


if __name__ == "__main__":
    main()
