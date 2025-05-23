using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
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
using RWParcer.Settings;
using RWParcerCore.InterfaceAdapters.Facades;
using Telegram.Bot;

namespace RWParcer
{
    public class Program
    {
        public static async Task Main(string[] args)
        {
            var builder = WebApplication.CreateBuilder(args);

            var port = Environment.GetEnvironmentVariable("PORT") ?? "8080";
            builder.WebHost.UseUrls($"http://0.0.0.0:{port}");

            const string secretPath = "/etc/secrets/appsettings.json";
            if (File.Exists(secretPath))
            {
                builder.Configuration.AddJsonFile(secretPath, optional: false, reloadOnChange: true);
            }
            else
            {
                builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
            }

            builder.Services.Configure<BotSettings>(builder.Configuration.GetSection("BotSettings"));
            builder.Services.Configure<DatabaseSettings>(builder.Configuration.GetSection("DatabaseSettings"));
            builder.Services.Configure<ProxySettings>(builder.Configuration.GetSection("ProxySettings"));

            builder.Services.AddScoped<ISessionManager, SessionManager>();

            builder.Services.AddSingleton<ITelegramBotClient>(sp =>
            {
                var settings = sp.GetRequiredService<IOptions<BotSettings>>().Value;
                return new TelegramBotClient(settings.ApiToken);
            });

            builder.Services.AddSingleton<ISessionStore, JsonSessionStore>();
            builder.Services.AddSingleton<IFacade>(sp =>
            {
                var dbSettings = sp.GetRequiredService<IOptions<DatabaseSettings>>().Value;
                var proxySettings = sp.GetRequiredService<IOptions<ProxySettings>>().Value;
                return new Facade(dbSettings.ConnectionString, proxySettings.ProxyAddresses);
            });
            builder.Services.AddTransient<ICommandRouter, CommandRouter>();

            builder.Services.AddSingleton<MainMenuProvider>();
            builder.Services.AddSingleton<TrainActionsProvider>();
            builder.Services.AddSingleton<SubscribeDateChoiceProvider>();
            builder.Services.AddSingleton<SubscriptionActionsProvider>();
            builder.Services.AddSingleton<UnsubscribeDateChoiceProvider>();
            builder.Services.AddSingleton<ManageUsersChoiceProvider>();
            builder.Services.AddSingleton<ModeratorChoiceProvider>();
            builder.Services.AddSingleton<ModeratorChooseSpanProvider>();

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
                                    typeof(ResetSubscriptionHandler),
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
                builder.Services.AddTransient(handler);
            }

            builder.Services.AddHostedService<BotService>();

            var app = builder.Build();
            app.MapGet("/", () => "Bot is running");

            await app.RunAsync();
        }
    }
}