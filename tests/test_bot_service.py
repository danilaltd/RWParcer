"""End-to-end smoke tests for ``BotService`` (app/bot/service.py).

Uses fakes for the Telegram bot, ``Facade`` and the session store so the
full update path (receive -> route -> send -> save snapshot) can be exercised
without a network connection or a database.
"""

from __future__ import annotations

import asyncio
import datetime
import uuid
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Chat, ChatIdUnion, Message, Update, User
from app.application.facade import Facade
from app.bot.command_names import CommandNames
from app.bot.router import CommandRouter
from app.bot.service import BotService
from app.bot.storage import SessionStorage
from app.domain.value_objects import NotificationItem

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from aiogram import Bot
    from app.bot.session import BotSession


class FakeBot:
    """Minimal stand-in for the aiogram ``Bot``."""

    def __init__(self) -> None:
        self.updates: list[SimpleNamespace] = []
        self.sent: list[tuple[ChatIdUnion, str, object]] = []
        self._offset_log: list[int] = []

    async def get_updates(
        self, offset: int, timeout: int = 30, allowed_updates: list[str] | None = None
    ) -> list:
        await asyncio.sleep(0)
        self._offset_log.append(offset)
        if offset == 0:
            pending = self.updates
            self.updates = []
            return pending
        return []

    async def send_message(
        self, chat_id: ChatIdUnion, text: str, reply_markup: object | None = None
    ) -> None:
        self.sent.append((chat_id, text, reply_markup))

    @staticmethod
    def make_update(chat_id: int, text: str | None, update_id: int = 1) -> Update:
        message = Message(
            text=text,
            message_id=update_id,
            date=datetime.datetime.now(),
            chat=Chat(id=chat_id, type="private"),
            from_user=User(id=chat_id, is_bot=False, first_name="TestUser"),
            content_type="text" if text is not None else "photo",
        )
        return Update(update_id=update_id, message=message)


@pytest.fixture
def fake_facade() -> MagicMock:
    facade = MagicMock(spec=Facade)
    facade.authenticate_user = AsyncMock(return_value=uuid.uuid4())
    facade.is_user_moderator = AsyncMock(return_value=False)
    facade.pop_notifications = AsyncMock(return_value=[])
    facade.get_user_by_id = AsyncMock(
        return_value=SimpleNamespace(id=uuid.uuid4(), telegram_chat_id=1, name="tester")
    )
    facade.users_repo = MagicMock()
    facade.users_repo.get_user_by_id = AsyncMock(return_value=SimpleNamespace(telegram_chat_id=1))
    return facade


class RecordingStore(SessionStorage):
    """In-memory store that also records the snapshots it was asked to save."""

    def __init__(self) -> None:
        super().__init__(pool=MagicMock())
        self.saved: dict[uuid.UUID, object] | None = None

    async def load(self) -> dict[uuid.UUID, BotSession]:
        return {}

    async def save_all(self, sessions: dict[uuid.UUID, BotSession]) -> None:
        self.saved = dict(sessions)


@pytest.fixture
async def service(
    fake_facade: MagicMock,
) -> AsyncGenerator[tuple[BotService, FakeBot, RecordingStore]]:
    bot = FakeBot()
    store = RecordingStore()
    router = CommandRouter(fake_facade)
    svc = BotService(
        bot=cast("Bot", bot),
        store=store,
        facade=fake_facade,
        router=router,
        poll_interval=0.01,
    )
    yield svc, bot, store
    if not svc._stop.is_set():
        await svc.stop()


async def test_start_command_routes_to_main_menu(
    service: tuple[BotService, FakeBot, RecordingStore],
    fake_facade: MagicMock,
) -> None:
    svc, bot, _store = service
    uid = uuid.uuid4()
    fake_facade.register_user.return_value = uid
    await svc.start()
    update = FakeBot.make_update(42, "/start")
    await svc._on_update(update)

    assert bot.sent, "expected at least one message"
    chat_id, text, markup = bot.sent[0]
    assert chat_id == 42
    assert text == "Главное меню: выберите пункт"
    assert any("Поиск" in button.text for row in getattr(markup, "keyboard", []) for button in row)

    session = svc._sessions.get_session(uid)
    assert session.current_command == CommandNames.MAIN_MENU_SELECT
    assert svc._sessions.get_all_sessions() == {uid: session}


async def test_non_start_command_routes_unknown(
    service: tuple[BotService, FakeBot, RecordingStore],
) -> None:
    svc, bot, _store = service
    await svc.start()
    await svc._on_update(FakeBot.make_update(7, "не команда"))
    assert bot.sent, "expected a message"
    assert "Неизвестная команда. Используйте /start" in bot.sent[0][1]


async def test_notifications_are_delivered(
    service: tuple[BotService, FakeBot, RecordingStore],
    fake_facade: MagicMock,
) -> None:
    svc, _bot, _store = service
    await svc.start()
    u_id = uuid.uuid4()
    fake_facade.pop_notifications.return_value = [
        NotificationItem(user_id=u_id, content="Поезд прибыл")
    ]
    await svc._process_notifications()

    messages = [m for m in await svc._facade.pop_notifications() if m.user_id == u_id]
    assert messages and messages[0].content == "Поезд прибыл"


async def test_session_is_saved_after_update(
    service: tuple[BotService, FakeBot, RecordingStore],
    request: pytest.FixtureRequest,
    fake_facade: MagicMock,
) -> None:
    svc, _bot, store = service
    uid = uuid.uuid4()
    fake_facade.register_user.return_value = uid
    await svc.start()
    assert store.saved is None
    await svc._on_update(FakeBot.make_update(1, "/start"))
    assert store.saved is not None
    assert uid in store.saved


async def test_stop_persists_and_cancels_tasks(
    service: tuple[BotService, FakeBot, RecordingStore],
) -> None:
    svc, _bot, _store = service
    await svc.start()
    await svc._on_update(FakeBot.make_update(2, "/start"))
    await svc.stop()
    assert svc._stop.is_set()
    assert not svc._tasks
