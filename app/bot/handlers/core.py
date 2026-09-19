"""Core/root handlers: ``StartHandler``, ``UnknownHandler``, ``MenuSelectHandler``,
``FeedbackHandler``, ``GetStatusHandler``, ``ViewMessagesHandler``.

Each mirrors the identically named file in ``RWParcer/Services/Handlers/``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.bot.command_names import CommandNames
from app.bot.converters import message_to_string, user_to_string

if TYPE_CHECKING:
    from app.application.facade import Facade
    from app.bot.context import CommandContext
    from app.bot.interfaces import ICommandRouter, IMenuProvider


class StartHandler:
    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        await self._facade.authenticate_user(ctx.chat_id)
        ctx.session.reset()
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)


class UnknownHandler:
    async def handle(self, ctx: CommandContext) -> None:
        await ctx.send_message("Неизвестная команда. Используйте /start")


class MenuSelectHandler:
    def __init__(self, router: ICommandRouter, menu: IMenuProvider, menu_head: str) -> None:
        self._router = router
        self._menu = menu
        self._menu_head = menu_head

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            options = await self._menu.get_options(ctx)
            await ctx.send_keyboard(options.keys(), self._menu_head)
            return

        options = await self._menu.get_options(ctx)
        if ctx.input in options:
            ctx.session.set_command(options[ctx.input])
            await self._router.route(options[ctx.input], ctx)
        else:
            await ctx.send_keyboard(
                options.keys(), "Неверный ввод. Пожалуйста, выберите пункт из меню:"
            )


class FeedbackHandler:
    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await ctx.send_message("Введите сообщение:")
            return

        await self._facade.send_feedback(ctx.chat_id, ctx.input)
        await ctx.send_message("Сообщние отправлено")
        ctx.session.data.clear()
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)


class GetStatusHandler:
    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        user = await self._facade.get_user_by_id(ctx.chat_id, ctx.chat_id)
        await ctx.send_message("Ваш статус: " + user_to_string(user))
        ctx.session.data.clear()
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)


class ViewMessagesHandler:
    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        messages = await self._facade.get_messages(ctx.chat_id)
        if messages:
            text = "Все сообщения:\n\n"
            text += "\n\n".join(message_to_string(m) for m in messages)
            await ctx.send_message(text)
        else:
            await ctx.send_message("Нет сообщений")
        ctx.session.data.clear()
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)
