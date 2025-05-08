using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using RWParcer.Handlers;
using RWParcer.Handlers.Search;
using RWParcer.Interfaces;
using RWParcer.MenuProviders;
using RWParcerCore.InterfaceAdapters.Facades;
using Telegram.Bot;
using RWParcer.Handlers.Favorites;
using RWParcer.Handlers.TrainsMenu.Favorites;
using RWParcer.Handlers.TrainsMenu.Subscribe;
using RWParcer.Handlers.TrainsMenu.Unsubscribe;
using RWParcer.Handlers.Subscriptions;
using Microsoft.Extensions.Options;
using RWParcer.Handlers.Moderator;

namespace RWParcer
{
    public class Program
    {
        public static async Task Main()
        {
            var host = Host.CreateDefaultBuilder()
                            .ConfigureAppConfiguration(config =>
                            {
                                var defaultPath = "appsettings.json";

                                var secretPath = "/etc/secrets/appsettings.json";

                                if (File.Exists(secretPath))
                                {
                                    config.AddJsonFile(secretPath, optional: false, reloadOnChange: true);
                                }
                                else if (File.Exists(defaultPath))
                                {
                                    config.AddJsonFile(defaultPath, optional: false, reloadOnChange: true);
                                }
                            })
                            .ConfigureServices((context, services) =>
                            {
                                services.Configure<BotSettings>(context.Configuration.GetSection("BotSettings"));

                                services.AddScoped<ISessionManager, SessionManager>();

                                services.AddSingleton<ITelegramBotClient>(sp =>
                                {
                                    var settings = sp.GetRequiredService<IOptions<BotSettings>>().Value;
                                    return new TelegramBotClient(settings.ApiToken);
                                });
                                services.AddSingleton<ISessionStore, JsonSessionStore>();
                                services.AddSingleton<IFacade, Facade>();
                                services.AddTransient<ICommandRouter, CommandRouter>();

                                services.AddSingleton<MainMenuProvider>();
                                services.AddSingleton<TrainActionsProvider>();
                                services.AddSingleton<SubscribeDateChoiceProvider>();
                                services.AddSingleton<SubscriptionActionsProvider>();
                                services.AddSingleton<UnsubscribeDateChoiceProvider>();
                                services.AddSingleton<ManageUsersChoiceProvider>();
                                services.AddSingleton<ModeratorChoiceProvider>();
                                services.AddSingleton<ModeratorChooseSpanProvider>();


                                var commandHandlers = new[]
                                {
                                    typeof(StartHandler),
                                    typeof(MenuSelectHandler),
                                    typeof(FromSelectHandler),
                                    typeof(AddToFavoritesHandler),
                                    typeof(RemoveFromFavoritesHandler),
                                    typeof(ToSelectHandler),
                                    typeof(TrainSearchSelectHandler),
                                    typeof(UnknownHandler),
                                    typeof(SubscribeEnterDateHandler),
                                    typeof(SubscribeUseLastDateHandler),
                                    typeof(SubscribeEnterDateRnageHandler),
                                    typeof(UnsubscribeEnterDateHandler),
                                    typeof(UnsubscribeUseLastDateHandler),
                                    typeof(UnsubscribeEnterDateRangeHandler),
                                    typeof(FavoritesSelectHandler),
                                    typeof(SubscriptionsSelectHandler),
                                    typeof(UnsubscribeSubscriptionHandler),
                                    typeof(ModeratorEnterSpanHandler),
                                    typeof(SelectUserHandler),
                                    typeof(ChangeUserMinIntervalLimitHandler),
                                    typeof(ChangeUserMaxSubscribtionLimitHandler),
                                    typeof(PromoteUserHandler),
                                    typeof(DemoteUserHandler),
                                    typeof(UnbanUserHandler),
                                    typeof(BanUserHandler),
                                    typeof(GetStatusHandler),
                                    typeof(FeedbackHandler),
                                    typeof(SendMessageEnterMessageHandler),
                                    typeof(ViewAllMessagesHandler),
                                    typeof(ViewMessagesHandler),
                                    typeof(ModeratorSpanHandler),
                                };

                                foreach (var handler in commandHandlers)
                                {
                                    services.AddTransient(handler);
                                }

                                services.AddHostedService<BotService>();
                            })
                            .Build();
            host.Services.GetRequiredService<IFacade>();
            await host.RunAsync();
        }
    }
}