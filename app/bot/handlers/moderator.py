"""Moderator flow: span pick/enter, user selection, user actions.

Ported from ``RWParcer/Services/Handlers/Moderator/*.cs``.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from app.application.facade import Facade
from app.bot.command_names import CommandNames
from app.bot.converters import message_to_string, user_to_string
from app.bot.dates import parse_timespan
from app.bot.interfaces import ICommandRouter
from app.domain.value_objects import UserInfo

if TYPE_CHECKING:
    from app.bot.context import CommandContext


class ModeratorSpanHandler:
    """``ModeratorSpanHandler(ICommandRouter, TimeSpan)`` — fixed spans."""

    def __init__(self, router: ICommandRouter, span: datetime.timedelta) -> None:
        self._router = router
        self._span = span

    async def handle(self, ctx: CommandContext) -> None:
        ctx.session.data.append(self._span)
        ctx.session.set_command(CommandNames.SELECT_USER)
        await self._router.route(CommandNames.SELECT_USER, ctx)


class ModeratorEnterSpanHandler:
    """``ModeratorEnterSpanHandler`` — free-form ``d*.hh:mm:ss`` input."""

    def __init__(self, router: ICommandRouter) -> None:
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await ctx.send_message("Введите промежуток времени в формате d*.hh:mm:ss")
            return

        ts = parse_timespan(ctx.input)
        if ts is None or ts == datetime.timedelta(0):
            await ctx.send_message("Неверный формат времени, используйте d*.hh:mm:ss")
            return

        ctx.session.data.append(ts)
        ctx.session.set_command(CommandNames.SELECT_USER)
        await self._router.route(CommandNames.SELECT_USER, ctx)


class SelectUserHandler:
    """``SelectUserHandler`` — users active within the chosen span."""

    def __init__(self, router: ICommandRouter, facade: Facade) -> None:
        self._router = router
        self._facade = facade

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await self._init_users(ctx)
            return

        await self._handle_selection(ctx)

    async def _init_users(self, ctx: CommandContext) -> None:
        ts = next((d for d in ctx.session.data if isinstance(d, datetime.timedelta)), None)
        if ts is None or ts == datetime.timedelta(0):
            await ctx.reset_session("Ошибка. Начните заново", self._router)
            return

        users = await self._facade.get_users(ctx.chat_id, ts)
        if not users:
            await ctx.reset_session("Нет пользователей за данный промежуток", self._router)
            return

        ctx.session.data.clear()
        ctx.session.data.append(users)
        await ctx.send_keyboard(
            [user_to_string(u) for u in users],
            "Выберите пользователя:",
            wrapping=True,
        )

    async def _handle_selection(self, ctx: CommandContext) -> None:
        users = next(
            (
                d
                for d in ctx.session.data
                if isinstance(d, list) and (not d or isinstance(d[0], UserInfo))
            ),
            None,
        )
        if users is None:
            await ctx.reset_session("Сессия устарела, начните заново", self._router)
            return

        if not ctx.input.strip():
            await ctx.send_message("Выберите пользователя из списка клавиатуры")
            return

        try:
            index = int(ctx.input)
        except ValueError:
            await ctx.send_message("Введите корректный индекс пользователя")
            return
        if not 1 <= index <= len(users):
            await ctx.send_message("Введите корректный индекс пользователя")
            return

        selected = users[index - 1]
        ctx.session.data.clear()
        ctx.session.data.append(selected)
        await ctx.send_message(f"Вы выбрали пользователя: {user_to_string(selected)}")
        ctx.session.set_command(CommandNames.MANAGE_USER_MENU_SELECT)
        await self._router.route(CommandNames.MANAGE_USER_MENU_SELECT, ctx)


class SendMessageEnterMessageHandler:
    """``SendMessageEnterMessageHandler`` — moderator writes to a user."""

    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await ctx.send_message("Введите сообщение:")
            return

        user = next((d for d in ctx.session.data if isinstance(d, UserInfo)), None)
        if user is None:
            ctx.session.reset()
            await ctx.send_message("Сессия устарела — начните заново")
            return

        await self._facade.send_message(ctx.chat_id, user.id, ctx.input)
        await ctx.send_message("Сообщение отправлено")

        ctx.session.data.clear()
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)


class _UserActionBase:
    """Promote/demote/ban/unban — shared guard + back-to-menu."""

    _message = ""

    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def _selected_user(self, ctx: CommandContext) -> UserInfo | None:
        user = next((d for d in ctx.session.data if isinstance(d, UserInfo)), None)
        if user is None:
            ctx.session.reset()
            await ctx.send_message("Сессия устарела — начните заново")
        return user

    async def handle(self, ctx: CommandContext) -> None:
        user = await self._selected_user(ctx)
        if user is None:
            return

        await self._act(ctx.chat_id, user.id)
        await ctx.send_message(self._message)
        ctx.session.data.clear()
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)

    async def _act(self, user_id: str, target_id: str) -> None:
        raise NotImplementedError


class PromoteUserHandler(_UserActionBase):
    _message = "Пользователь повышен до модератора"

    async def _act(self, user_id: str, target_id: str) -> None:
        await self._facade.promote_user(user_id, target_id)


class DemoteUserHandler(_UserActionBase):
    _message = "Модератор понижен до пользователя"

    async def _act(self, user_id: str, target_id: str) -> None:
        await self._facade.demote_user(user_id, target_id)


class BanUserHandler(_UserActionBase):
    _message = "Пользователь забанен"

    async def _act(self, user_id: str, target_id: str) -> None:
        await self._facade.ban_user(user_id, target_id)


class UnbanUserHandler(_UserActionBase):
    _message = "Пользователь разбанен"

    async def _act(self, user_id: str, target_id: str) -> None:
        await self._facade.unban_user(user_id, target_id)


class ChangeUserMinIntervalLimitHandler:
    """``ChangeUserMinIntervalLimitHandler`` — positive integer input."""

    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await ctx.send_message("Введите целое положительное число")
            return

        user = next((d for d in ctx.session.data if isinstance(d, UserInfo)), None)
        if user is None:
            ctx.session.reset()
            await ctx.send_message("Сессия устарела — начните заново")
            return

        num = self._parse_uint(ctx.input)
        if num is None or num < 1:
            await ctx.send_message("Неверный формат, введите целое положительное число")
            return

        await self._facade.set_users_min_interval(ctx.chat_id, user.id, num)
        await ctx.send_message("Минимальный интервал проверки для пользователя установлен")
        ctx.session.data.clear()
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)

    @staticmethod
    def _parse_uint(text: str) -> int | None:
        value = text.strip()
        if not value or not value.isdigit():
            return None
        return int(value)


class ChangeUserMaxSubscribtionLimitHandler:
    """``ChangeUserMaxSubscribtionLimitHandler`` — ``uint`` input (may be 0)."""

    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await ctx.send_message("Введите целое неотрицательное число")
            return

        user = next((d for d in ctx.session.data if isinstance(d, UserInfo)), None)
        if user is None:
            ctx.session.reset()
            await ctx.send_message("Сессия устарела — начните заново")
            return

        num = self._parse_uint(ctx.input)
        if num is None:
            await ctx.send_message("Неверный формат, введите целое неотрицательное число")
            return

        await self._facade.set_users_max_subscriptions(ctx.chat_id, user.id, num)
        await ctx.send_message("Максимальное число подписок для пользователя установлен")
        ctx.session.data.clear()
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)

    @staticmethod
    def _parse_uint(text: str) -> int | None:
        value = text.strip()
        if not value or not value.isdigit():
            return None
        return int(value)


class ViewAllMessagesHandler:
    """``ViewAllMessagesHandler`` — moderator sees every user's messages."""

    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        messages = await self._facade.get_all_messages(ctx.chat_id)
        if messages:
            text = "Все сообщения:\n\n"
            text += "\n\n".join(message_to_string(m) for m in messages)
            await ctx.send_message(text)
        else:
            await ctx.send_message("Нет сообщений")
        ctx.session.data.clear()
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)
