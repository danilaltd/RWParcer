"""Subscriptions list flow: pick a subscription, unsubscribe or reset it.

Ported from ``RWParcer/Services/Handlers/Subscriptions/*.cs``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.bot.command_names import CommandNames
from app.bot.converters import subscription_to_string
from app.domain.value_objects import SubscriptionDetails

if TYPE_CHECKING:
    from app.application.facade import Facade
    from app.bot.context import CommandContext
    from app.bot.interfaces import ICommandRouter


def _is_subscription_list(value: object) -> bool:
    return isinstance(value, list) and (not value or isinstance(value[0], SubscriptionDetails))


class SubscriptionsSelectHandler:
    def __init__(self, router: ICommandRouter, facade: Facade) -> None:
        self._router = router
        self._facade = facade

    async def handle(self, ctx: CommandContext) -> None:
        if ctx.session.init_state:
            await self._init_subscriptions(ctx)
            return

        await self._handle_selection(ctx)

    async def _init_subscriptions(self, ctx: CommandContext) -> None:
        subscriptions = await self._facade.get_subscriptions(ctx.user_id, ctx.user_id)
        if not subscriptions:
            await ctx.reset_session("Нет подписок", self._router)
            return

        ctx.session.data.clear()
        ctx.session.data.append(subscriptions)
        await ctx.send_keyboard(
            [subscription_to_string(s) for s in subscriptions],
            "Выберите подписку:",
            wrapping=True,
        )

    async def _handle_selection(self, ctx: CommandContext) -> None:
        subscriptions = next((d for d in ctx.session.data if _is_subscription_list(d)), None)
        if subscriptions is None:
            await ctx.reset_session("Сессия устарела, начните заново", self._router)
            return

        if not ctx.input.strip():
            await ctx.send_message("Выберите поезд из списка клавиатуры")
            return

        try:
            index = int(ctx.input)
        except ValueError:
            await ctx.send_message("Введите корректный индекс подписки")
            return
        if not 1 <= index <= len(subscriptions):
            await ctx.send_message("Введите корректный индекс подписки")
            return

        selected = subscriptions[index - 1]
        ctx.session.data.clear()
        ctx.session.data.append(selected)
        await ctx.send_message(f"Вы выбрали подписку: {subscription_to_string(selected)}")
        ctx.session.set_command(CommandNames.SUBSCRIPTION_MENU_SELECT)
        await self._router.route(CommandNames.SUBSCRIPTION_MENU_SELECT, ctx)


class UnsubscribeSubscriptionHandler:
    """C# ``UnsubscribeSubscriptionHandler`` — "Отписка выполнена"."""

    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        # C# ``Data.OfType<SubscriptionVO>().First()``.
        subscription = next(d for d in ctx.session.data if isinstance(d, SubscriptionDetails))
        await self._facade.unsubscribe(ctx.user_id, subscription)
        await ctx.send_message("Отписка выполнена")
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)


class ResetSubscriptionHandler:
    """C# ``ResetSubscriptionHandler`` — "Сброс выполнен"."""

    def __init__(self, facade: Facade, router: ICommandRouter) -> None:
        self._facade = facade
        self._router = router

    async def handle(self, ctx: CommandContext) -> None:
        # C# ``Data.OfType<SubscriptionVO>().First()``.
        subscription = next(d for d in ctx.session.data if isinstance(d, SubscriptionDetails))
        await self._facade.reset_subscription(ctx.user_id, subscription)
        await ctx.send_message("Сброс выполнен")
        ctx.session.set_command(CommandNames.MAIN_MENU_SELECT)
        await self._router.route(CommandNames.MAIN_MENU_SELECT, ctx)
