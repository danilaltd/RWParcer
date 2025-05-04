using RWParcer.Interfaces;
using Telegram.Bot;
using Telegram.Bot.Types.ReplyMarkups;

namespace RWParcer
{
    public class CommandContext
    {
        public string ChatId { get; }
        public string Input { get; }
        public UserSession Session { get; }
        public ITelegramBotClient Bot { get; }
        public CancellationToken Token { get; }

        public CommandContext(string chatId, string input, UserSession session, ITelegramBotClient bot, CancellationToken token)
        {
            ChatId = chatId;
            Input = input;
            Session = session;
            Bot = bot;
            Token = token;
        }

        public Task SendMessage(string text)
            => Bot.SendMessage(ChatId, text, cancellationToken: Token);

        public Task SendKeyboard(IEnumerable<string> options, string prompt, bool wrapping = false)
        {
            KeyboardButton[][] buttons;

            if (wrapping)
            {
                prompt += '\n' + string.Join("\n", options.Take(174).Select((label, index) => $"{index + 1} {label}"));
                buttons = options.Select((label, index) => new KeyboardButton[] { new((index + 1).ToString()) }).ToArray();
            }
            else
            {
                buttons = options.Take(174).Select(label => new KeyboardButton[] { new(label) }).ToArray();
            }

            var keyboard = new ReplyKeyboardMarkup(buttons)
            {
                ResizeKeyboard = true,
                OneTimeKeyboard = true
            };

            return Bot.SendMessage(ChatId, prompt, replyMarkup: keyboard, cancellationToken: Token);
        }

        public async Task ResetSessionAsync(string message, ICommandRouter router)
        {
            Session.Reset();
            await Bot.SendMessage(ChatId, message);
            Session.SetCommand(CommandNames.MainMenuSelect);
            await router.RouteAsync(CommandNames.MainMenuSelect, this);
        }
    }
}