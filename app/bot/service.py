"""``BotService`` — mirrors ``RWParcer/Services/BotService.cs``.

* sessions are loaded once at startup (``_sessions = _store.Load()``);
* every text update routes through the ``CommandRouter`` keyed by the
  session's current command (``/start`` always resets and starts over);
* the full in-memory session table is rewritten after every update;
* a loop polls ``PopNotificationsAsync`` every ``poll_interval`` seconds and
  delivers notifications directly to the user chats.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Sequence
from typing import Any

from aiogram import Bot
from aiogram.enums import ContentType
from app.application.errors import UnauthorizedError
from app.application.facade import Facade
from app.bot.command_names import CommandNames
from app.bot.context import CommandContext
from app.bot.router import CommandRouter
from app.bot.storage import BotSessionManager, SessionStorage

logger = logging.getLogger(__name__)

BACKEND_ERROR_MESSAGE = "Backend Error. Попробуйте снова"


class BotService:
    """Long-poll front end that mirrors the C# ``BackgroundService``."""

    def __init__(
        self,
        bot: Bot,
        store: SessionStorage,
        facade: Facade,
        router: CommandRouter,
        allowed_updates: Sequence[str] = ("Message",),
        poll_interval: float = 5.0,
    ) -> None:
        self._bot = bot
        self._store = store
        self._facade = facade
        self._router = router
        self._allowed_updates = [str(item).lower() for item in allowed_updates]
        self._poll_interval = poll_interval
        self._sessions = BotSessionManager()
        self._stop = asyncio.Event()
        self._tasks: list[asyncio.Task] = []

    # ------------------------------------------------------------------
    # lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """``BotService`` construction: load persisted sessions first."""
        self._sessions = BotSessionManager(await self._store.load())
        self._tasks = [
            asyncio.create_task(self._receive_loop(), name="bot-receive"),
            asyncio.create_task(self._notifications_loop(), name="bot-notify"),
        ]

    async def wait(self) -> None:
        await self._stop.wait()

    async def stop(self) -> None:
        if self._stop.is_set():
            return
        self._stop.set()
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks = []
        # C# ``StopAsync`` persists before shutting down.
        try:
            await self._store.save_all(self._sessions.get_all_sessions())
        except Exception as exc:  # noqa: BLE001 - C# did not guard either
            logger.warning("Error saving sessions on stop: %s", exc)

    # ------------------------------------------------------------------
    # Update flow (``OnUpdate`` / ``ReceiveAsync``)
    # ------------------------------------------------------------------

    async def _receive_loop(self) -> None:
        """``_bot.StartReceiving(OnUpdate, OnError, ReceiverOptions{...})``."""
        offset = 0
        while not self._stop.is_set():
            try:
                updates = await self._bot.get_updates(
                    offset=offset,
                    timeout=30,
                    allowed_updates=self._allowed_updates,
                )
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - ``OnError``
                logger.error("Error receiving updates: %s", exc)
                await asyncio.sleep(1)
                continue
            for update in updates:
                offset = update.update_id + 1
                try:
                    await self._on_update(update)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:  # noqa: BLE001 - ``OnError``
                    logger.error("Error handling update: %s", exc)

    async def _on_update(self, update: Any) -> None:
        """Port of ``OnUpdate`` (the ``update.Message.Type == Text`` branch)."""
        message = update.message
        if message is None or message.content_type != ContentType.TEXT:
            return
        if message.text is None:
            return
        text = message.text.strip()
        chat_id = str(message.chat.id)
        session = self._sessions.get_session(chat_id)
        ctx = CommandContext(chat_id, text, session, self._bot, message)
        try:
            if text.lower() == "/start":
                session.reset()
                await self._router.route(CommandNames.START, ctx)
            else:
                command = (
                    session.current_command
                    if session.current_command is not None
                    else CommandNames.UNKNOWN
                )
                await self._router.route(command, ctx)
        except UnauthorizedError:
            raise
        except Exception as exc:  # noqa: BLE001 - C# ``catch when not Unauthorized``
            await ctx.reset_session(BACKEND_ERROR_MESSAGE, self._router)
            logger.error("%s", exc)
        finally:
            await self._store.save_all(self._sessions.get_all_sessions())

    # ------------------------------------------------------------------
    # Notifications loop (``ProcessNotificationsAsync``)
    # ------------------------------------------------------------------

    async def _notifications_loop(self) -> None:
        while not self._stop.is_set():
            await self._process_notifications()
            try:
                await asyncio.sleep(self._poll_interval)
            except asyncio.CancelledError:
                raise

    async def _process_notifications(self) -> None:
        notifications = await self._facade.pop_notifications()
        for notification in notifications or []:
            session = self._sessions.get_session(notification.user_id)
            ctx = CommandContext(notification.user_id, "", session, self._bot)
            await ctx.send_notification(notification.content)
