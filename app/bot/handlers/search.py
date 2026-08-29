"""Train-search flow: from/to station pick + train selection.

Ported from ``RWParcer/Services/Handlers/Search/{FromSelect,ToSelect,
TrainSearchSelect}Handler.cs``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.application.facade import Facade
from app.bot.command_names import CommandNames
from app.bot.converters import convert_train
from app.bot.handlers.base import BaseTrainsHandler, StationSelectHandler
from app.bot.interfaces import ICommandRouter
from app.domain.value_objects import Route, Station

if TYPE_CHECKING:
    from app.bot.context import CommandContext


class FromSelectHandler(StationSelectHandler):
    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        super().__init__(
            facade,
            router,
            CommandNames.TO_SELECT,
            "Введите префикс станции отправления:",
            "Станция отправления выбрана: {0}",
        )


class ToSelectHandler(StationSelectHandler):
    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        super().__init__(
            facade,
            router,
            CommandNames.TRAIN_SELECT,
            "Введите префикс станции назначения:",
            "Станция назначения выбрана: {0}",
        )


class TrainSearchSelectHandler(BaseTrainsHandler):
    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await self._init_routes(ctx)
            return

        await self.handle_train_selection(ctx)

    async def _init_routes(self, ctx: CommandContext) -> None:
        stations = [d for d in ctx.session.data if isinstance(d, Station)]
        if len(stations) != 2:
            await ctx.reset_session("Ошибка выбора станции. Начните заново", self._router)
            return

        trains = await self._facade.get_times_for_route(
            ctx.chat_id, Route(stations[0], stations[1])
        )
        if not trains:
            await ctx.reset_session("Поезда не найдены", self._router)
            return

        ctx.session.data.clear()
        ctx.session.data.append(trains)
        await ctx.send_keyboard(
            [convert_train(t) for t in trains], "Выберите поезд:", wrapping=True
        )
