"""BotService handling Telegram updates, user resolution, and session persistence."""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import TYPE_CHECKING

from aiogram.enums import ContentType
from app.application.errors import UnauthorizedError
from app.bot.command_names import CommandNames
from app.bot.context import CommandContext
from app.bot.storage import BotSessionManager, SessionStorage

if TYPE_CHECKING:
    from collections.abc import Sequence

    from aiogram import Bot
    from aiogram.types import Update
    from app.application.facade import Facade
    from app.bot.router import CommandRouter

logger = logging.getLogger(__name__)

BACKEND_ERROR_MESSAGE = "Backend Error. Попробуйте снова"


class BotService:
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

    async def start(self) -> None:
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
        try:
            await self._store.save_all(self._sessions.get_all_sessions())
        except Exception as exc:
            logger.warning("Error saving sessions on stop: %s", exc)

    async def _receive_loop(self) -> None:
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
            except Exception as exc:
                logger.error("Error receiving updates: %s", exc)
                await asyncio.sleep(1)
                continue
            for update in updates:
                offset = update.update_id + 1
                try:
                    await self._on_update(update)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    logger.error("Error handling update: %s", exc)

    async def _on_update(self, update: Update) -> None:
        message = update.message
        if message is None or message.content_type != ContentType.TEXT:
            return
        if message.text is None or message.from_user is None:
            return
        text = message.text.strip()
        chat_id = str(message.chat.id)
        telegram_user_id = message.from_user.id
        telegram_chat_id = message.chat.id

        user_id = await self._facade.authenticate_user(telegram_user_id, telegram_chat_id)
        session = self._sessions.get_session(user_id)
        ctx = CommandContext(chat_id, user_id, text, session, self._bot, message)
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
        except Exception as exc:
            await ctx.reset_session(BACKEND_ERROR_MESSAGE, self._router)
            logger.exception(exc)
        finally:
            await self._store.save_all(self._sessions.get_all_sessions())

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
            try:
                u_id = uuid.UUID(notification.user_id)
            except ValueError:
                continue
            session = self._sessions.get_session(u_id)
            user_obj = await self._facade.users_repo.get_user_by_id(u_id)
            chat_id = (
                str(user_obj.telegram_chat_id)
                if user_obj and user_obj.telegram_chat_id
                else str(u_id)
            )
            ctx = CommandContext(chat_id, u_id, "", session, self._bot)
            await ctx.send_notification(notification.content)
