"""Subscribe-by-date flow from the train menu.

Ported from ``RWParcer/Services/Handlers/TrainsMenu/Subscribe/*.cs``
(including the ``SubscribeEnterDateRnageHandler`` filename typo's logic).
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from app.bot.command_names import CommandNames
from app.bot.dates import add_months, parse_date_exact
from app.domain.value_objects import SubscriptionDetails, Train

if TYPE_CHECKING:
    from app.application.facade import Facade
    from app.bot.context import CommandContext
    from app.bot.interfaces import ICommandRouter


class _SubscribeBase:
    """Shared plumbing: train lookup + back-to-main-menu routing."""

    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def _back_to_menu(self, ctx: CommandContext) -> None:
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)


class SubscribeEnterDateHandler(_SubscribeBase):
    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await ctx.send_message("Введите дату в формате DD.MM.YYYY")
            return

        date = parse_date_exact(ctx.input)
        if date is None:
            await ctx.send_message("Неверный формат даты, используйте DD.MM.YYYY")
            return

        today = datetime.date.today()
        if date < today:
            await ctx.send_message("Эта дата уже прошла. Укажите актуальную дату")
            return
        if date > add_months(today, 3):
            await ctx.send_message("Эта дата наступит нескоро. Укажите актуальную дату")
            return

        train = next(d for d in ctx.session.data if isinstance(d, Train))
        ctx.session.date = date
        try:
            await self._facade.subscribe(ctx.user_id, SubscriptionDetails(train, date))
            await ctx.send_message(f"Подписка установлена на {date:%d.%m.%Y}")
        except RuntimeError:
            await ctx.send_message(f"Подписка на дату {date:%d.%m.%Y} уже существует")
        except OverflowError:
            await ctx.send_message("Вы достигли лимита подписок")
        await self._back_to_menu(ctx)


class SubscribeUseLastDateHandler(_SubscribeBase):
    async def handle(self, ctx: CommandContext) -> None:
        today = datetime.date.today()
        if ctx.session.date < today:
            await ctx.send_message("Эта дата уже прошла. Возврат в главное меню")
            await self._back_to_menu(ctx)
            return

        if ctx.session.date > add_months(today, 3):
            await ctx.send_message("Эта дата наступит нескоро. Укажите актуальную дату")
            return

        train = next(d for d in ctx.session.data if isinstance(d, Train))
        try:
            await self._facade.subscribe(ctx.user_id, SubscriptionDetails(train, ctx.session.date))
            await ctx.send_message(f"Подписка установлена на {ctx.session.date:%d.%m.%Y}")
        except RuntimeError:
            await ctx.send_message(f"Подписка на дату {ctx.session.date:%d.%m.%Y} уже существует")
        except OverflowError:
            await ctx.send_message("Вы достигли лимита подписок")
        await self._back_to_menu(ctx)


class SubscribeEnterDateRangeHandler(_SubscribeBase):
    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await ctx.send_message("Введите диапазон в формате DD.MM.YYYY-DD.MM.YYYY")
            return

        dates = ctx.input.split("-")
        start_date = parse_date_exact(dates[0].strip()) if len(dates) == 2 else None
        end_date = parse_date_exact(dates[1].strip()) if len(dates) == 2 else None
        if start_date is None or end_date is None or start_date > end_date:
            await ctx.send_message("Неверный формат диапазона, используйте DD.MM.YYYY-DD.MM.YYYY")
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
                await self._facade.subscribe(ctx.user_id, SubscriptionDetails(train, date))
            except RuntimeError:
                ans += f"Подписка на дату {date:%d.%m.%Y} уже существует\n"
            except OverflowError:
                ans += "Вы достигли лимита подписок"
                end_date = date - datetime.timedelta(days=1)
                break
            date += datetime.timedelta(days=1)

        await ctx.send_message(
            f"Подписка выполнена выполнена на {start_date:%d.%m.%Y} - {end_date:%d.%m.%Y}"
            + (f"\n{ans}" if ans else "")
        )
        await self._back_to_menu(ctx)
