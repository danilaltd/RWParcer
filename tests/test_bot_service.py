"""End-to-end smoke tests for ``BotService`` (app/bot/service.py).

Uses fakes for the Telegram bot, ``Facade`` and the session store so the
full update path (receive -> route -> send -> save snapshot) can be exercised
without a network connection or a database.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Bot
from app.application.facade import Facade
from app.bot.router import CommandRouter
from app.bot.service import BotService
from app.bot.session import BotSession
from app.bot.storage import SessionStorage
from app.domain.value_objects import NotificationItem


class FakeBot:
    """Minimal stand-in for the aiogram ``Bot``."""

    def __init__(self) -> None:
        self.updates: list[SimpleNamespace] = []
        self.sent: list[tuple[str, str, object]] = []
        self._offset_log: list[int] = []

    async def get_updates(self, offset, timeout=30, allowed_updates=None) -> list:
        await asyncio.sleep(0)
        self._offset_log.append(offset)
        if offset == 0:
            pending = self.updates
            self.updates = []
            return pending
        return []

    async def send_message(self, chat_id: str, text: str, reply_markup=None) -> None:
        self.sent.append((chat_id, text, reply_markup))

    @staticmethod
    def make_update(chat_id: str, text: str | None, update_id: int = 1) -> SimpleNamespace:
        message = SimpleNamespace(
            text=text,
            chat=SimpleNamespace(id=chat_id),
            content_type="text" if text is not None else "photo",
        )
        return SimpleNamespace(update_id=update_id, message=message)


@pytest.fixture
def fake_facade() -> MagicMock:
    facade = MagicMock(spec=Facade)
    facade.authenticate_user = AsyncMock()
    facade.is_user_moderator = AsyncMock(return_value=False)
    facade.pop_notifications = AsyncMock(return_value=[])
    facade.get_user_by_id = AsyncMock(
        return_value=SimpleNamespace(id="1", name="tester")
    )
    return facade


class RecordingStore(SessionStorage):
    """In-memory store that also records the snapshots it was asked to save."""

    def __init__(self) -> None:
        super().__init__(session_factory=None)
        self.saved: dict[str, object] | None = None

    async def load(self) -> dict[str, BotSession]:
        return {}

    async def save_all(self, sessions: dict[str, BotSession]) -> None:
        self.saved = dict(sessions)


@pytest.fixture
async def service(
    fake_facade: MagicMock,
) -> AsyncGenerator[tuple[BotService, FakeBot, RecordingStore], None]:
    bot = FakeBot()
    store = RecordingStore()
    router = CommandRouter(fake_facade)
    svc = BotService(
        bot=cast(Bot, bot),
        store=store,
        facade=fake_facade,
        router=router,
        poll_interval=0.01,
    )
    yield svc, bot, store
    if not svc._stop.is_set():
        await svc.stop()


async def test_start_command_routes_to_main_menu(service) -> None:
    svc, bot, _store = service
    await svc.start()
    update = FakeBot.make_update("42", "/start")
    await svc._on_update(update)

    assert bot.sent, "expected at least one message"
    chat_id, text, markup = bot.sent[0]
    assert chat_id == "42"
    assert text == "Главное меню: выберите пункт"
    assert any(
        "Поиск" in button.text
        for row in getattr(markup, "keyboard", [])
        for button in row
    )

    session = svc._sessions.get_session("42")
    assert session.current_command.name == "MAIN_MENU_SELECT"
    assert svc._sessions.get_all_sessions() == {"42": session}


async def test_non_start_command_routes_unknown(service) -> None:
    svc, bot, _store = service
    await svc.start()
    await svc._on_update(FakeBot.make_update("7", "не команда"))
    assert bot.sent, "expected a message"
    assert "Неизвестная команда. Используйте /start" in bot.sent[0][1]


async def test_notifications_are_delivered(service, fake_facade) -> None:
    svc, _bot, _store = service
    await svc.start()
    fake_facade.pop_notifications.return_value = [
        NotificationItem(user_id="55", content="Поезд прибыл")
    ]
    await svc._process_notifications()

    messages = [m for m in svc._bot.sent if m[0] == "55"]
    assert messages and messages[0][1] == "Поезд прибыл"


async def test_session_is_saved_after_update(service, request) -> None:
    svc, _bot, store = service
    await svc.start()
    assert store.saved is None
    await svc._on_update(FakeBot.make_update("1", "/start"))
    assert store.saved is not None
    assert "1" in store.saved


async def test_stop_persists_and_cancels_tasks(service) -> None:
    svc, _bot, _store = service
    await svc.start()
    await svc._on_update(FakeBot.make_update("2", "/start"))
    await svc.stop()
    assert svc._stop.is_set()
    assert not svc._tasks
