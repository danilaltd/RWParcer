using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;
using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;
using System.Diagnostics;
using Telegram.Bot;
using Telegram.Bot.Polling;
using Telegram.Bot.Types;
using Telegram.Bot.Types.Enums;

namespace RWParcer
{
    public class BotService : BackgroundService
    {
        private readonly ITelegramBotClient _bot;
        private readonly ICommandRouter _router;
        private readonly ISessionManager _sessions;
        private readonly BotSettings _settings;
        private readonly ISessionStore _store;
        private readonly IFacade _facade;

        public BotService(
            ITelegramBotClient bot,
            ICommandRouter router,
            ISessionStore store,
            IOptions<BotSettings> options,
            IFacade facade)
        {
            _bot = bot;
            _router = router;
            //_sessions = store.Load();
            _sessions = new SessionManager();
            _store = store;
            _settings = options.Value;
            _facade = facade;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _ = Task.Run(() => _bot.StartReceiving(
                OnUpdate,
                OnError,
                new ReceiverOptions { AllowedUpdates = _settings.AllowedUpdates },
                cancellationToken: stoppingToken), stoppingToken);
            while (!stoppingToken.IsCancellationRequested)
            {
                await ProcessNotificationsAsync(stoppingToken);
                try
                {
                    await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken); // Проверяем уведомления каждые 5 секунд
                }
                catch { }
            }
        }

        private async Task OnUpdate(ITelegramBotClient client, Update update, CancellationToken token)
        {
            if (update.Message?.Type != MessageType.Text) return;

            var chatId = update.Message.Chat.Id.ToString();
            if (update.Message.Text == null) return;
            var text = update.Message.Text.Trim();
            var session = _sessions.GetSession(chatId);
            var ctx = new CommandContext(chatId, text, session, client, token);

            try
            {
                if (text.Equals("/start", StringComparison.OrdinalIgnoreCase))
                {
                    session.Reset();
                    await _router.RouteAsync(CommandNames.Start, ctx);
                }
                else
                {
                    await _router.RouteAsync(session.CurrentCommand ?? CommandNames.Unknown, ctx);
                }
            }
            catch (Exception ex) when (!(ex is UnauthorizedAccessException))
            {
                await ctx.ResetSessionAsync("Backend Error. Попробуйте снова", _router);
                Console.WriteLine(ex.Message);
            }
            finally
            {
                await _store.SaveAsync(_sessions);

            }
        }

        private async Task ProcessNotificationsAsync(CancellationToken token)
        {
            var notifications = await _facade.PopNotificationsAsync();
            if (notifications == null || notifications.Count == 0) return;
            foreach (var notification in notifications)
            {
                var session = _sessions.GetSession(notification.UserId);
                var ctx = new CommandContext(notification.UserId, "", session, _bot, token);
                await ctx.SendMessage(notification.Content);
            }
        }

        private Task OnError(ITelegramBotClient client, Exception ex, CancellationToken token)
        {
            Console.WriteLine(ex);
            return Task.CompletedTask;
        }

        public override Task StopAsync(CancellationToken cancellationToken)
        {
            _store.Save(_sessions);
            return base.StopAsync(cancellationToken);
        }
    }
}