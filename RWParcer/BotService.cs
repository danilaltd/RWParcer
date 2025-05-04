using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;
using RWParcer.Interfaces;
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

        public BotService(
            ITelegramBotClient bot,
            ICommandRouter router,
            ISessionStore store,
            IOptions<BotSettings> options)
        {
            _bot = bot;
            _router = router;
            //_sessions = store.Load();
            _sessions = new SessionManager();
            _store = store;
            _settings = options.Value;
        }

        protected override Task ExecuteAsync(CancellationToken stoppingToken)
        {
            _bot.StartReceiving(
                OnUpdate,
                OnError,
                new ReceiverOptions { AllowedUpdates = _settings.AllowedUpdates },
                cancellationToken: stoppingToken);

            return Task.CompletedTask;
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
            catch (Exception ex)
            {
                await ctx.ResetSessionAsync("Backend Error. Попробуйте снова.", _router);
            }
            finally
            {
                await _store.SaveAsync(_sessions);

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