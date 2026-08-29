"""Unsubscribe-by-date flows from the train menu.

Ported from ``RWParcer/Services/Handlers/TrainsMenu/Unsubscribe/*.cs``.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from app.application.errors import InvalidOperationError
from app.application.facade import Facade
from app.bot.command_names import CommandNames
from app.bot.dates import add_months, parse_date_exact
from app.bot.interfaces import ICommandRouter
from app.domain.value_objects import SubscriptionDetails, Train

if TYPE_CHECKING:
    from app.bot.context import CommandContext


class UnsubscribeEnterDateHandler:
    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await ctx.send_message("Введите дату в формате DD.MM.YYYY")
            return

        date = parse_date_exact(ctx.input)
        if date is None:
            await ctx.send_message("Неверный формат даты, используйте DD.MM.YYYY")
            return

        train = next(d for d in ctx.session.data if isinstance(d, Train))
        ctx.session.date = date

        try:
            await self._facade.unsubscribe(ctx.chat_id, SubscriptionDetails(train, date))
            await ctx.send_message(f"Отписка выполнена на {date:%d.%m.%Y}")
        except InvalidOperationError:
            await ctx.send_message(f"Подписка на дату {date:%d.%m.%Y} не существует")

        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)


class UnsubscribeUseLastDateHandler:
    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        train = next(d for d in ctx.session.data if isinstance(d, Train))
        try:
            await self._facade.unsubscribe(
                ctx.chat_id, SubscriptionDetails(train, ctx.session.date)
            )
            await ctx.send_message(f"Отписка выполнена на {ctx.session.date:%d.%m.%Y}")
        except InvalidOperationError:
            await ctx.send_message(
                f"Подписка на дату {ctx.session.date:%d.%m.%Y} не существует"
            )

        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)


class UnsubscribeEnterDateRangeHandler:
    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await ctx.send_message("Введите диапазон в формате DD.MM.YYYY-DD.MM.YYYY")
            return

        dates = ctx.input.split("-")
        start_date = parse_date_exact(dates[0].strip()) if len(dates) == 2 else None
        end_date = parse_date_exact(dates[1].strip()) if len(dates) == 2 else None
        if start_date is None or end_date is None or start_date > end_date:
            await ctx.send_message(
                "Неверный формат диапазона, используйте DD.MM.YYYY-DD.MM.YYYY"
            )
            return

        if (end_date - start_date).days >= 60:
            await ctx.send_message("Слишком большой диапазон")
            return

        today = datetime.date.today()
        if start_date < today:
            await ctx.send_message("Эта дата уже прошла. Укажите актуальную дату")
            return
        if end_date > add_months(today, 3):
            await ctx.send_message("Эта дата наступит нескоро. Укажите актуальную дату")
            return

        train = next(d for d in ctx.session.data if isinstance(d, Train))
        ans = ""
        date = start_date
        while date <= end_date:
            try:
                await self._facade.unsubscribe(
                    ctx.chat_id, SubscriptionDetails(train, date)
                )
            except InvalidOperationError:
                ans += f"Подписка на дату {date:%d.%m.%Y} не существует\n"
            date += datetime.timedelta(days=1)

        await ctx.send_message(
            f"Отписка выполнена на {start_date:%d.%m.%Y} - {end_date:%d.%m.%Y}"
            + (f"\n{ans}" if ans else "")
        )

        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)
