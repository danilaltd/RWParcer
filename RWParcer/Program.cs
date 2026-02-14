using Microsoft.Extensions.Hosting;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;
using RWParcer.Configuration;
using RWParcer.Infrastructure.Database;
using RWParcer.Infrastructure.Session;
using RWParcer.Interfaces;
using RWParcer.Services;
using RWParcer.Services.Commands;
using RWParcer.Services.Handlers;
using RWParcer.Services.Handlers.Favorites;
using RWParcer.Services.Handlers.Moderator;
using RWParcer.Services.Handlers.Search;
using RWParcer.Services.Handlers.Subscriptions;
using RWParcer.Services.Handlers.TrainsMenu.Favorites;
using RWParcer.Services.Handlers.TrainsMenu.Subscribe;
using RWParcer.Services.Handlers.TrainsMenu.Unsubscribe;
using RWParcer.Services.Menu;
using RWParcerCore.InterfaceAdapters.Facades;
using Telegram.Bot;

namespace RWParcer
{
    public class Program
    {
        public static async Task Main(string[] args)
        {
            var builder = Host.CreateApplicationBuilder(args);

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

            var facade = new Facade(
                builder.Services.BuildServiceProvider().GetRequiredService<IOptions<DatabaseSettings>>().Value.ConnectionString,
                builder.Services.BuildServiceProvider().GetRequiredService<IOptions<ProxySettings>>().Value.ProxyAddresses
            );
            builder.Services.AddSingleton<IFacade>(facade);
            
            builder.Services.AddDbContext<SessionDbContext>(options =>
                options.UseNpgsql(builder.Services.BuildServiceProvider()
                    .GetRequiredService<IOptions<DatabaseSettings>>()
                    .Value.SessionConnectionString));
            //builder.Services.AddDbContext<SessionDbContext>(options =>
            //    options.UseSqlite(builder.Services.BuildServiceProvider()
            //        .GetRequiredService<IOptions<DatabaseSettings>>()
            //        .Value.SessionConnectionString));

            builder.Services.AddSingleton<SessionDbContextFactory>();
            builder.Services.AddSingleton<ISessionStore, PostgresSessionStore>();
            //builder.Services.AddSingleton<ISessionStore, SqliteSessionStore>();
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

            using IHost host = builder.Build();
            await host.RunAsync();
        }
    }
}