"""CommandContext wrapping bot, user_id, chat_id, and session."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from app.bot.command_names import CommandNames

if TYPE_CHECKING:
    import uuid
    from collections.abc import Iterable

    from aiogram import Bot
    from app.bot.interfaces import ICommandRouter
    from app.bot.session import BotSession

logger = logging.getLogger(__name__)


class CommandContext:
    """Per-update context handed to every command handler."""

    def __init__(
        self,
        chat_id: int,
        user_id: uuid.UUID,
        input: str,
        session: BotSession,
        bot: Bot,
        message: Message | None = None,
    ) -> None:
        self._chat_id = chat_id
        self._user_id = user_id
        self._input = input
        self._session = session
        self._bot = bot
        self._message = message

    @property
    def chat_id(self) -> int:
        return self._chat_id

    @property
    def user_id(self) -> uuid.UUID:
        return self._user_id

    @property
    def input(self) -> str:
        return self._input

    @property
    def session(self) -> BotSession:
        return self._session

    @property
    def bot(self) -> Bot:
        return self._bot

    async def send_message(self, text: str) -> None:
        await self._send_to_client(text, reply_markup=ReplyKeyboardRemove())

    async def send_notification(self, text: str) -> None:
        await self._send_to_client(text, reply_markup=None)

    async def send_keyboard(
        self, options: Iterable[str], prompt: str, wrapping: bool = False
    ) -> None:
        options = list(options)
        if wrapping:
            prompt += "\n" + "\n\n".join(
                f"{index + 1} {label}" for index, label in enumerate(options[:174])
            )
            buttons = [[KeyboardButton(text=str(index + 1))] for index in range(len(options))]
        else:
            buttons = [[KeyboardButton(text=label)] for label in options[:174]]

        keyboard = ReplyKeyboardMarkup(
            keyboard=buttons, resize_keyboard=True, one_time_keyboard=True
        )
        await self._send_to_client(prompt, reply_markup=keyboard)

    async def reset_session(self, message: str, router: ICommandRouter) -> None:
        self._session.reset()
        await self.send_message(message)
        self._session.set_command(CommandNames.MAIN_MENU_SELECT)
        await router.route(CommandNames.MAIN_MENU_SELECT, self)

    async def _send_to_client(
        self, text: str, reply_markup: ReplyKeyboardMarkup | ReplyKeyboardRemove | None
    ) -> None:
        try:
            for chunk in self.split_message_smart(text, 4096):
                await self._bot.send_message(self._chat_id, chunk, reply_markup=reply_markup)
        except Exception as exc:
            logger.warning("Error sending message for chat %s: %s", self._chat_id, exc)

    @staticmethod
    def split_message_smart(
        message: str,
        max_length: int,
        candidate_delimiters: list[str] | None = None,
    ) -> list[str]:
        candidate_delimiters = candidate_delimiters or ["\n\n", "\n", " "]
        chosen = next((d for d in candidate_delimiters if d in message), " ")
        delimiter = chosen if chosen in candidate_delimiters else " "

        blocks = [block.strip() for block in message.split(delimiter) if block.strip()]

        hard_split: list[str] = []
        for block in blocks:
            if len(block) <= max_length:
                hard_split.append(block)
                continue
            pos = 0
            while pos < len(block):
                end = min(pos + max_length, len(block))
                split = -1
                for token in candidate_delimiters:
                    idx = block.rfind(token, pos, end)
                    if idx > pos:
                        split = idx + len(token)
                        break
                if split <= pos:
                    split = end
                hard_split.append(block[pos:split])
                pos = split

        result: list[str] = []
        current = ""
        for chunk in hard_split:
            if not current:
                current = chunk
            elif len(current) + len(delimiter) + len(chunk) <= max_length:
                current += delimiter + chunk
            else:
                result.append(current)
                current = chunk
        if current:
            result.append(current)
        return result
