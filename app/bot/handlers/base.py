"""Shared handler bases, ported from the C# handler hierarchy.

``StationSelectHandler`` is ``RWParcer/Services/Handlers/Search/StationSelectHandler.cs``;
``BaseTrainsHandler`` is ``RWParcer/Services/Handlers/BaseTrainsHandler.cs``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.bot.command_names import CommandNames
from app.bot.converters import convert_train
from app.bot.interfaces import ICommandHandler, ICommandRouter
from app.domain.value_objects import Station, Train

if TYPE_CHECKING:
    from app.application.facade import Facade
    from app.bot.context import CommandContext


def _is_station_list(value: object) -> bool:
    """Runtime stand-in for the C# generic type ``List<StationVO>``."""
    return isinstance(value, list) and (not value or isinstance(value[0], Station))


def _is_train_list(value: object) -> bool:
    """Runtime stand-in for the C# generic type ``List<TrainVO>``."""
    return isinstance(value, list) and (not value or isinstance(value[0], Train))


class StationSelectHandler(ICommandHandler):
    """Abstract station-prefix selection with a label-pick fallback.

    Ordered argument list matches the C# primary constructor
    ``(IFacade, ICommandRouter, CommandNames, string, string)``.
    """

    def __init__(
        self,
        facade: Facade,
        router: ICommandRouter,
        next_command: CommandNames,
        prompt_text: str,
        keyboard_text: str,
    ) -> None:
        self._facade = facade
        self._router = router
        self._next_command = next_command
        self._prompt_text = prompt_text
        self._keyboard_text = keyboard_text

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await ctx.send_message(self._prompt_text)
            return

        existing = [d for d in ctx.session.data if isinstance(d, Station)]
        last_list = next((d for d in ctx.session.data if _is_station_list(d)), None)

        if last_list is not None and any(s.label == ctx.input for s in last_list):
            chosen = next(s for s in last_list if s.label == ctx.input)
            ctx.session.data.clear()
            ctx.session.data.extend(existing)
            ctx.session.data.append(chosen)
            ctx.session.set_command(self._next_command)
            await ctx.send_message(self._keyboard_text.format(chosen.label))
            await self._router.route(self._next_command, ctx)
            return

        candidates = await self._facade.get_station(ctx.user_id, ctx.input)
        if not candidates:
            await ctx.send_message(f"Станции не найдены. {self._prompt_text}")
            return

        ctx.session.data[:] = [d for d in ctx.session.data if not _is_station_list(d)]
        ctx.session.data.append(candidates)
        await ctx.send_keyboard(
            [s.label for s in candidates],
            f"Выберите станцию из списка\nИЛИ\n{self._prompt_text}",
        )


class BaseTrainsHandler(ICommandHandler):
    """C# ``BaseTrainsHandler`` — numbered train-pick flow shared by search/favorites."""

    def __init__(self, router: ICommandRouter, facade: Facade) -> None:
        self._router = router
        self._facade = facade

    async def handle(self, ctx: CommandContext) -> None:
        raise NotImplementedError

    async def handle_train_selection(self, ctx: CommandContext) -> None:
        trains_list = next((d for d in ctx.session.data if _is_train_list(d)), None)
        if trains_list is None:
            await ctx.reset_session("Сессия устарела, начните заново", self._router)
            return

        if not ctx.input.strip():
            await ctx.send_message("Выберите поезд из списка клавиатуры")
            return

        try:
            index = int(ctx.input)
        except ValueError:
            await ctx.send_message("Введите корректный индекс поезда")
            return
        if not 1 <= index <= len(trains_list):
            await ctx.send_message("Введите корректный индекс поезда")
            return

        selected = trains_list[index - 1]
        ctx.session.data.clear()
        ctx.session.data.append(selected)
        await ctx.send_message(f"Вы выбрали поезд: {convert_train(selected)}")
        ctx.session.set_command(CommandNames.TRAIN_MENU_SELECT)
        await self._router.route(CommandNames.TRAIN_MENU_SELECT, ctx)
