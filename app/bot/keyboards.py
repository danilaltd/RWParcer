"""Menu providers, ported from ``RWParcer/Services/Menu/*MenuProvider.cs``.

Each provider returns ``label -> next CommandNames`` pairs used by
``MenuSelectHandler``. Labels and prompts are kept byte-for-byte identical
to the C# source.
"""

from __future__ import annotations

from app.bot.command_names import CommandNames
from app.bot.context import CommandContext
from app.bot.interfaces import IMenuProvider
from app.domain.value_objects import Station, SubscriptionDetails, Train, UserInfo


class MainMenuProvider(IMenuProvider):
    def __init__(self, facade) -> None:
        self._facade = facade

    async def get_options(self, ctx: CommandContext) -> dict[str, CommandNames]:
        options: dict[str, CommandNames] = {
            "🔍 Поиск": CommandNames.FROM_SELECT,
            "⭐ Избранное": CommandNames.FAVORITES_SELECT,
            "📢 Подписки": CommandNames.SUBSCRIPTIONS_SELECT,
            "👤 Мой статус": CommandNames.GET_STATUS,
            "📨 Мои сообщения": CommandNames.VIEW_MESSAGES,
            "💬 Обратная связь": CommandNames.FEEDBACK,
        }
        if await self._facade.is_user_moderator(ctx.chat_id, ctx.chat_id):
            options["👮 Меню модератора"] = CommandNames.MODERATOR_MENU_SELECT
        return options


class ManageUsersChoiceProvider(IMenuProvider):
    def __init__(self, facade) -> None:
        self._facade = facade

    async def get_options(self, ctx: CommandContext) -> dict[str, CommandNames]:
        user = next(
            (d for d in ctx.session.data if isinstance(d, UserInfo)), None
        )
        if user is None:
            raise RuntimeError("Session has no selected user")
        options: dict[str, CommandNames] = {}
        if await self._facade.is_user_moderator(ctx.chat_id, user.id):
            options["⬇️ Понизить до пользователя"] = CommandNames.DEMOTE_USER
        else:
            options["⬆️ Повысить до модератора"] = CommandNames.PROMOTE_USER

        if await self._facade.is_user_banned(ctx.chat_id, user.id):
            options["✅ Разбанить"] = CommandNames.UNBAN_USER
        else:
            options["🚫 Забанить"] = CommandNames.BAN_USER

        options["📊 Лимит подписок"] = CommandNames.CHANGE_USER_MAX_SUBSCRIPTION_LIMIT
        options["⏱️ Интервал проверки"] = CommandNames.CHANGE_USER_MIN_INTERVAL_LIMIT
        options["✉️ Отправить сообщение"] = CommandNames.SEND_MESSAGE_ENTER_MESSAGE
        options["🏠 В главное меню"] = CommandNames.MAIN_MENU_SELECT
        return options


class ModeratorChoiceProvider(IMenuProvider):
    async def get_options(self, ctx: CommandContext) -> dict[str, CommandNames]:
        return {
            "📊 Статистика пользователей": CommandNames.MODERATOR_SPAN_SELECT,
            "📨 Все сообщения": CommandNames.VIEW_ALL_MESSAGES,
        }


class ModeratorChooseSpanProvider(IMenuProvider):
    async def get_options(self, ctx: CommandContext) -> dict[str, CommandNames]:
        return {
            "📅 Ввести период": CommandNames.MODERATOR_ENTER_SPAN,
            "⏱️ Последняя минута": CommandNames.MODERATOR_SPAN_MINUTE,
            "🕐 Последний час": CommandNames.MODERATOR_SPAN_HOUR,
            "📆 Последний день": CommandNames.MODERATOR_SPAN_DAY,
        }


class SubscribeDateChoiceProvider(IMenuProvider):
    async def get_options(self, ctx: CommandContext) -> dict[str, CommandNames]:
        return {
            "📅 Ввести дату": CommandNames.SUBSCRIBE_ENTER_DATE,
            f"🕒 Последняя дата: {ctx.session.date}": CommandNames.SUBSCRIBE_USE_LAST_DATE,
            "📆 Ввести диапазон": CommandNames.SUBSCRIBE_ENTER_DATE_RANGE,
            "🏠 В главное меню": CommandNames.MAIN_MENU_SELECT,
        }


class UnsubscribeDateChoiceProvider(IMenuProvider):
    async def get_options(self, ctx: CommandContext) -> dict[str, CommandNames]:
        return {
            "📅 Ввести дату": CommandNames.UNSUBSCRIBE_ENTER_DATE,
            f"🕒 Использовать последнюю дату: {ctx.session.date}": CommandNames.UNSUBSCRIBE_USE_LAST_DATE,
            "Ввести диапазон": CommandNames.UNSUBSCRIBE_ENTER_DATE_RANGE,
            "🏠 В главное меню": CommandNames.MAIN_MENU_SELECT,
        }


class TrainActionsProvider(IMenuProvider):
    def __init__(self, facade) -> None:
        self._facade = facade

    async def get_options(self, ctx: CommandContext) -> dict[str, CommandNames]:
        train = next(
            (d for d in ctx.session.data if isinstance(d, Train)), None
        )
        if train is None:
            raise RuntimeError("Session has no train")

        options: dict[str, CommandNames] = {}
        if await self._facade.is_in_favorites(ctx.chat_id, train):
            options["⭐ Удалить из избранного"] = CommandNames.REMOVE_FROM_FAVORITES
        else:
            options["⭐ Добавить в избранное"] = CommandNames.ADD_TO_FAVORITES

        options["🔔 Подписаться"] = CommandNames.SUBSCRIBE_DATE_SELECT
        options["🚫 Отписаться"] = CommandNames.UNSUBSCRIBE_DATE_SELECT
        options["🏠 В главное меню"] = CommandNames.MAIN_MENU_SELECT
        return options


class SubscriptionActionsProvider(IMenuProvider):
    async def get_options(self, ctx: CommandContext) -> dict[str, CommandNames]:
        return {
            "🚫 Отписаться": CommandNames.UNSUBSCRIBE_SUBSCRIPTION,
            "🔄 Сбросить состояние": CommandNames.RESET_SUBSCRIPTION,
            "🏠 В главное меню": CommandNames.MAIN_MENU_SELECT,
        }


def first_of_type(data: list, target: type, default=None):
    return next((d for d in data if isinstance(d, target)), default)


__all__ = [
    "MainMenuProvider",
    "ManageUsersChoiceProvider",
    "ModeratorChoiceProvider",
    "ModeratorChooseSpanProvider",
    "SubscribeDateChoiceProvider",
    "UnsubscribeDateChoiceProvider",
    "TrainActionsProvider",
    "SubscriptionActionsProvider",
    "first_of_type",
]