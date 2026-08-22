"""Command factories, mirroring ``RWParcer/Services/Commands/CommandRouter.cs``.

Every handler gets its dependencies at construction time (the Python stand-in
for the C# ``IServiceProvider``), including the ``MenuSelectHandler`` closures
that pair a menu provider with its fixed head string.
"""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from app.bot.command_names import CommandNames
from app.bot.handlers.core import (
    FeedbackHandler,
    GetStatusHandler,
    MenuSelectHandler,
    StartHandler,
    UnknownHandler,
    ViewMessagesHandler,
)
from app.bot.handlers.favorites import (
    AddToFavoritesHandler,
    FavoritesSelectHandler,
    RemoveFromFavoritesHandler,
)
from app.bot.handlers.moderator import (
    BanUserHandler,
    ChangeUserMaxSubscribtionLimitHandler,
    ChangeUserMinIntervalLimitHandler,
    DemoteUserHandler,
    ModeratorEnterSpanHandler,
    ModeratorSpanHandler,
    PromoteUserHandler,
    SelectUserHandler,
    SendMessageEnterMessageHandler,
    UnbanUserHandler,
    ViewAllMessagesHandler,
)
from app.bot.handlers.search import (
    FromSelectHandler,
    ToSelectHandler,
    TrainSearchSelectHandler,
)
from app.bot.handlers.subscribe import (
    SubscribeEnterDateHandler,
    SubscribeEnterDateRangeHandler,
    SubscribeUseLastDateHandler,
)
from app.bot.handlers.subscriptions import (
    ResetSubscriptionHandler,
    SubscriptionsSelectHandler,
    UnsubscribeSubscriptionHandler,
)
from app.bot.handlers.unsubscribe import (
    UnsubscribeEnterDateHandler,
    UnsubscribeEnterDateRangeHandler,
    UnsubscribeUseLastDateHandler,
)
from app.bot.interfaces import ICommandHandler
from app.bot.keyboards import (
    MainMenuProvider,
    ManageUsersChoiceProvider,
    ModeratorChoiceProvider,
    ModeratorChooseSpanProvider,
    SubscribeDateChoiceProvider,
    SubscriptionActionsProvider,
    TrainActionsProvider,
    UnsubscribeDateChoiceProvider,
)

if TYPE_CHECKING:
    from app.bot.context import CommandContext


class CommandRouter:
    """Maps every ``CommandNames`` value to its handler (like the C# dict)."""

    def __init__(self, facade) -> None:
        self._map: dict[CommandNames, ICommandHandler] = {}
        self._build(facade)

    def _build(self, facade) -> None:
        self._map.update(
            {
                CommandNames.START: StartHandler(facade, self),
                CommandNames.MAIN_MENU_SELECT: MenuSelectHandler(
                    self,
                    MainMenuProvider(facade),
                    "Главное меню: выберите пункт",
                ),
                CommandNames.FROM_SELECT: FromSelectHandler(facade, self),
                CommandNames.TO_SELECT: ToSelectHandler(facade, self),
                CommandNames.TRAIN_SELECT: TrainSearchSelectHandler(self, facade),
                CommandNames.TRAIN_MENU_SELECT: MenuSelectHandler(
                    self,
                    TrainActionsProvider(facade),
                    "Что сделать с этим поездом? Выберите пункт меню",
                ),
                CommandNames.ADD_TO_FAVORITES: AddToFavoritesHandler(facade, self),
                CommandNames.REMOVE_FROM_FAVORITES: RemoveFromFavoritesHandler(
                    facade, self
                ),
                CommandNames.SUBSCRIBE_DATE_SELECT: MenuSelectHandler(
                    self,
                    SubscribeDateChoiceProvider(),
                    "Способ выбора даты? Выберите пункт меню",
                ),
                CommandNames.SUBSCRIBE_ENTER_DATE: SubscribeEnterDateHandler(
                    facade, self
                ),
                CommandNames.SUBSCRIBE_USE_LAST_DATE: SubscribeUseLastDateHandler(
                    facade, self
                ),
                CommandNames.SUBSCRIBE_ENTER_DATE_RANGE: SubscribeEnterDateRangeHandler(
                    facade, self
                ),
                CommandNames.UNSUBSCRIBE_DATE_SELECT: MenuSelectHandler(
                    self,
                    UnsubscribeDateChoiceProvider(),
                    "Способ выбора даты? Выберите пункт меню",
                ),
                CommandNames.UNSUBSCRIBE_ENTER_DATE: UnsubscribeEnterDateHandler(
                    facade, self
                ),
                CommandNames.UNSUBSCRIBE_USE_LAST_DATE: UnsubscribeUseLastDateHandler(
                    facade, self
                ),
                CommandNames.UNSUBSCRIBE_ENTER_DATE_RANGE: UnsubscribeEnterDateRangeHandler(
                    facade, self
                ),
                CommandNames.FAVORITES_SELECT: FavoritesSelectHandler(self, facade),
                CommandNames.SUBSCRIPTIONS_SELECT: SubscriptionsSelectHandler(
                    self, facade
                ),
                CommandNames.SUBSCRIPTION_MENU_SELECT: MenuSelectHandler(
                    self,
                    SubscriptionActionsProvider(),
                    "Что сделать с этой подпиской? Выберите пункт меню",
                ),
                CommandNames.UNSUBSCRIBE_SUBSCRIPTION: UnsubscribeSubscriptionHandler(
                    facade, self
                ),
                CommandNames.RESET_SUBSCRIPTION: ResetSubscriptionHandler(facade, self),
                CommandNames.UNKNOWN: UnknownHandler(),
                CommandNames.MODERATOR_SPAN_SELECT: MenuSelectHandler(
                    self,
                    ModeratorChooseSpanProvider(),
                    "Выберите команду промежуток",
                ),
                CommandNames.MODERATOR_ENTER_SPAN: ModeratorEnterSpanHandler(self),
                CommandNames.MODERATOR_SPAN_DAY: ModeratorSpanHandler(
                    self, datetime.timedelta(days=1)
                ),
                CommandNames.MODERATOR_SPAN_HOUR: ModeratorSpanHandler(
                    self, datetime.timedelta(hours=1)
                ),
                CommandNames.MODERATOR_SPAN_MINUTE: ModeratorSpanHandler(
                    self, datetime.timedelta(minutes=1)
                ),
                CommandNames.SELECT_USER: SelectUserHandler(self, facade),
                CommandNames.MODERATOR_MENU_SELECT: MenuSelectHandler(
                    self,
                    ModeratorChoiceProvider(),
                    "Выберите команду модератора",
                ),
                CommandNames.MANAGE_USER_MENU_SELECT: MenuSelectHandler(
                    self,
                    ManageUsersChoiceProvider(facade),
                    "Выберите команду модератора",
                ),
                CommandNames.VIEW_MESSAGES: ViewMessagesHandler(facade, self),
                CommandNames.VIEW_ALL_MESSAGES: ViewAllMessagesHandler(facade, self),
                CommandNames.SEND_MESSAGE_ENTER_MESSAGE: SendMessageEnterMessageHandler(
                    facade, self
                ),
                CommandNames.BAN_USER: BanUserHandler(facade, self),
                CommandNames.UNBAN_USER: UnbanUserHandler(facade, self),
                CommandNames.DEMOTE_USER: DemoteUserHandler(facade, self),
                CommandNames.PROMOTE_USER: PromoteUserHandler(facade, self),
                CommandNames.CHANGE_USER_MAX_SUBSCRIPTION_LIMIT: (
                    ChangeUserMaxSubscribtionLimitHandler(facade, self)
                ),
                CommandNames.CHANGE_USER_MIN_INTERVAL_LIMIT: (
                    ChangeUserMinIntervalLimitHandler(facade, self)
                ),
                CommandNames.GET_STATUS: GetStatusHandler(facade, self),
                CommandNames.FEEDBACK: FeedbackHandler(facade, self),
            }
        )

    async def route(self, cmd: CommandNames | None, ctx: CommandContext) -> None:
        """``RouteAsync`` — unknown commands fall back to ``UnknownHandler``."""
        handler = self._map.get(
            cmd if cmd is not None else CommandNames.UNKNOWN, self._map[CommandNames.UNKNOWN]
        )
        await handler.handle(ctx)
