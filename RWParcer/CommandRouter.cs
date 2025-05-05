using Microsoft.Extensions.DependencyInjection;
using RWParcer.Handlers;
using RWParcer.Handlers.Favorites;
using RWParcer.Handlers.Moderator;
using RWParcer.Handlers.Search;
using RWParcer.Handlers.Subscriptions;
using RWParcer.Handlers.TrainsMenu.Favorites;
using RWParcer.Handlers.TrainsMenu.Subscribe;
using RWParcer.Handlers.TrainsMenu.Unsubscribe;
using RWParcer.Interfaces;
using RWParcer.MenuProviders;

namespace RWParcer
{
    public class CommandRouter : ICommandRouter
    {
        private readonly IServiceProvider _sp;
        private readonly Dictionary<CommandNames, Func<IServiceProvider, ICommandHandler>> _map;

        public CommandRouter(IServiceProvider sp)
        {
            _sp = sp;
            _map = new Dictionary<CommandNames, Func<IServiceProvider, ICommandHandler>>
            {
                { CommandNames.Start,                  s => s.GetRequiredService<StartHandler>() },
                { CommandNames.MainMenuSelect,         s => {
                                                                var router = s.GetRequiredService<ICommandRouter>();
                                                                var menu = s.GetRequiredService<MainMenuProvider>();
                                                                return new MenuSelectHandler(router, menu, "Главное меню: выберите пункт");
                                                            }  },

                { CommandNames.FromSelect,             s => s.GetRequiredService<FromSelectHandler>() },
                { CommandNames.ToSelect,               s => s.GetRequiredService<ToSelectHandler>() },
                { CommandNames.TrainSelect,            s => s.GetRequiredService<TrainSearchSelectHandler>() },

                    { CommandNames.TrainMenuSelect,      s => {
                                                                    var router = s.GetRequiredService<ICommandRouter>();
                                                                    var menu = s.GetRequiredService<TrainActionsProvider>();
                                                                    return new MenuSelectHandler(router, menu, "Что сделать с этим поездом? Выберите пункт меню");
                                                                }  },
                        { CommandNames.AddToFavorites,           s => s.GetRequiredService<AddToFavoritesHandler>() },
                        { CommandNames.RemoveFromFavorites,      s => s.GetRequiredService<RemoveFromFavoritesHandler>() },

                        { CommandNames.SubscribeDateSelect,      s => {
                                                                        var router = s.GetRequiredService<ICommandRouter>();
                                                                        var menu = s.GetRequiredService<SubscribeDateChoiceProvider>();
                                                                        return new MenuSelectHandler(router, menu, "Способ выбора даты? Выберите пункт меню");
                                                                    }  },
                        { CommandNames.SubscribeEnterDate,     s => s.GetRequiredService<SubscribeEnterDateHandler>() },
                        //{ CommandNames.SubscribeUseLastDate,     s => s.GetRequiredService<SubscribeEnterDateHandler>() },
                

                        { CommandNames.UnsubscribeDateSelect,      s => {
                                                                        var router = s.GetRequiredService<ICommandRouter>();
                                                                        var menu = s.GetRequiredService<UnsubscribeDateChoiceProvider>();
                                                                        return new MenuSelectHandler(router, menu, "Способ выбора даты? Выберите пункт меню");
                                                                    }  },

                        { CommandNames.UnsubscribeEnterDate,   s => s.GetRequiredService<UnsubscribeEnterDateHandler>() },
                        //{ CommandNames.UnsubscribeUseLastDate,     s => s.GetRequiredService<SubscribeEnterDateHandler>() },

                
                
                { CommandNames.FavoritesSelect,             s => s.GetRequiredService<FavoritesSelectHandler>() },
                { CommandNames.SubscriptionsSelect,             s => s.GetRequiredService<SubscriptionsSelectHandler>() },

                { CommandNames.SubscriptionMenuSelect,      s => {
                                                                var router = s.GetRequiredService<ICommandRouter>();
                                                                var menu = s.GetRequiredService<SubscriptionActionsProvider>();
                                                                return new MenuSelectHandler(router, menu, "Что сделать с этой подпиской? Выберите пункт меню");
                                                                } },
                { CommandNames.UnsubscribeSubscription,  s => s.GetRequiredService<UnsubscribeSubscriptionHandler>() },
                { CommandNames.Unknown,                s => s.GetRequiredService<UnknownHandler>() },
                { CommandNames.ModeratorEnterSpan,                s => s.GetRequiredService<ModeratorEnterSpanHandler>() },
                { CommandNames.SelectUser,                s => s.GetRequiredService<SelectUserHandler>() },
                { CommandNames.        ModeratorMenuSelect,      s => {
                                                                var router = s.GetRequiredService<ICommandRouter>();
                                                                var menu = s.GetRequiredService<ModeratorChoiceProvider>();
                                                                return new MenuSelectHandler(router, menu, "Выберите команду модератора");
                                                                } },
                { CommandNames.ManageUserMenuSelect,      s => {
                                                                var router = s.GetRequiredService<ICommandRouter>();
                                                                var menu = s.GetRequiredService<ManageUsersChoiceProvider>();
                                                                return new MenuSelectHandler(router, menu, "Выберите команду модератора");
                                                                } },
                { CommandNames.ViewMessages,                s => s.GetRequiredService<ViewMessagesHandler>() },
                { CommandNames.ViewAllMessages,                s => s.GetRequiredService<ViewAllMessagesHandler>() },
                { CommandNames.SendMessageEnterMessage,                s => s.GetRequiredService<SendMessageEnterMessageHandler>() },
                { CommandNames.BanUser,                s => s.GetRequiredService<BanUserHandler>() },
                { CommandNames.UnbanUser,                s => s.GetRequiredService<UnbanUserHandler>() },
                { CommandNames.DemoteUser,                s => s.GetRequiredService<DemoteUserHandler>() },
                { CommandNames.PromoteUser,                s => s.GetRequiredService<PromoteUserHandler>() },
                { CommandNames.ChangeUserMaxSubscribtionLimit,                s => s.GetRequiredService<ChangeUserMaxSubscribtionLimitHandler>() },
                { CommandNames.ChangeUserMinIntervalLimit,                s => s.GetRequiredService<ChangeUserMinIntervalLimitHandler>() },
                { CommandNames.GetStatus,                s => s.GetRequiredService<GetStatusHandler>() },
                { CommandNames.Feedback,                s => s.GetRequiredService<FeedbackHandler>() },
            };

        }

        public async Task RouteAsync(CommandNames? cmd, CommandContext ctx)
        {
            if (!_map.TryGetValue(cmd ?? CommandNames.Unknown, out var factory)) factory = _map[CommandNames.Unknown];
            var handler = factory(_sp);
            await handler.HandleAsync(ctx);
        }
    }
}