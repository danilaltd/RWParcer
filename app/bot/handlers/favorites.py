"""Favorites flow: list selection + add/remove from the train menu.

Ported from ``RWParcer/Services/Handlers/Favorites/FavoritesSelectHandler.cs``
and ``RWParcer/Services/Handlers/TrainsMenu/Favorites/*.cs``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.bot.command_names import CommandNames
from app.bot.converters import convert_train
from app.bot.handlers.base import BaseTrainsHandler
from app.domain.value_objects import Train

if TYPE_CHECKING:
    from app.bot.context import CommandContext


class FavoritesSelectHandler(BaseTrainsHandler):
    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await self._init_favorites(ctx)
            return

        await self.handle_train_selection(ctx)

    async def _init_favorites(self, ctx: CommandContext) -> None:
        favorites = await self._facade.get_favorites(ctx.chat_id)
        if not favorites:
            await ctx.reset_session("В избранном пусто", self._router)
            return

        ctx.session.data.clear()
        ctx.session.data.append(favorites)
        await ctx.send_keyboard(
            [convert_train(t) for t in favorites], "Выберите элемент:", wrapping=True
        )


class _TrainMenuActionBase:
    """C# ``TrainsMenu.Favorites`` handlers — session guard, then act + menu."""

    def __init__(self, facade, router) -> None:
        self._facade = facade
        self._router = router

    async def _current_train(self, ctx: CommandContext) -> Train | None:
        train = next((d for d in ctx.session.data if isinstance(d, Train)), None)
        if train is None:
            ctx.session.reset()
            await ctx.send_message("Сессия устарела — начните заново")
        return train

    async def _back_to_menu(self, ctx: CommandContext) -> None:
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)


class AddToFavoritesHandler(_TrainMenuActionBase):
    async def handle(self, ctx: CommandContext) -> None:
        train = await self._current_train(ctx)
        if train is None:
            return

        await self._facade.add_to_favorites(ctx.chat_id, train)
        await ctx.send_message("Поезд добавлен в избранное!")
        await self._back_to_menu(ctx)


class RemoveFromFavoritesHandler(_TrainMenuActionBase):
    async def handle(self, ctx: CommandContext) -> None:
        train = await self._current_train(ctx)
        if train is None:
            return

        await self._facade.remove_from_favorites(ctx.chat_id, train)
        await ctx.send_message("Поезд удален из избранного!")
        await self._back_to_menu(ctx)
