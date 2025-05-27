using RWParcer.Interfaces;
using RWParcer.Models;
using System.Text;
using Telegram.Bot;
using Telegram.Bot.Types.ReplyMarkups;

namespace RWParcer.Services.Commands
{
    public class CommandContext(string chatId, string input, UserSession session, ITelegramBotClient bot, CancellationToken token)
    {
        public string ChatId { get; } = chatId;
        public string Input { get; } = input;
        public UserSession Session { get; } = session;
        public ITelegramBotClient Bot { get; } = bot;
        public CancellationToken Token { get; } = token;

        public Task SendMessage(string text)
            => SendMessageToClient(text, replyMarkup: new ReplyKeyboardRemove());

        public Task SendNotification(string text)
            => SendMessageToClient(text, replyMarkup: null);

        public Task SendKeyboard(IEnumerable<string> options, string prompt, bool wrapping = false)
        {
            KeyboardButton[][] buttons;

            if (wrapping)
            {
                prompt += '\n' + string.Join("\n\n", options.Take(174).Select((label, index) => $"{index + 1} {label}"));
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

            return SendMessageToClient(prompt, replyMarkup: keyboard);
        }

        public async Task ResetSessionAsync(string message, ICommandRouter router)
        {
            Session.Reset();
            await SendMessage(message);
            Session.SetCommand(CommandNames.MainMenuSelect);
            await router.RouteAsync(CommandNames.MainMenuSelect, this);
        }

        private async Task SendMessageToClient(string message, ReplyMarkup? replyMarkup = null)
        {
            const int maxLength = 4096;
            List<string> chunks = SplitMessageSmart(message, maxLength).ToList();

            foreach (var chunk in chunks)
            {
                await Bot.SendMessage(ChatId, chunk, replyMarkup: replyMarkup, cancellationToken: Token);
            }
        }


        public static IEnumerable<string> SplitMessageSmart(
    string message,
    int maxLength,
    string[]? candidateDelimiters = null)
        {
            candidateDelimiters ??= ["\n\n", "\n", " "];

            string chosenDelim = candidateDelimiters.FirstOrDefault(d => message.Contains(d)) ?? " ";
            string delim = chosenDelim ?? "";

            List<string> blocks;
            if (chosenDelim != null)
            {
                blocks = message
                    .Split([chosenDelim], StringSplitOptions.None)
                    .Select(s => s.Trim())
                    .Where(s => s.Length > 0)
                    .ToList();
            }
            else
            {
                blocks = new List<string> { message };
            }

            var hardSplit = new List<string>();
            foreach (var block in blocks)
            {
                if (block.Length <= maxLength)
                {
                    hardSplit.Add(block);
                }
                else
                {
                    int pos = 0;
                    while (pos < block.Length)
                    {
                        int end = Math.Min(pos + maxLength, block.Length);
                        int split = -1;
                        foreach (var token in candidateDelimiters)
                        {
                            int idx = block.LastIndexOf(token, end - 1, end - pos);
                            if (idx > pos)
                            {
                                split = idx + token.Length;
                                break;
                            }
                        }
                        if (split <= pos)
                            split = end;

                        hardSplit.Add(block.Substring(pos, split - pos));
                        pos = split;
                    }
                }
            }

            var current = new StringBuilder();
            foreach (var chunk in hardSplit)
            {
                if (current.Length == 0)
                {
                    current.Append(chunk);
                }
                else if (current.Length + delim.Length + chunk.Length <= maxLength)
                {
                    current.Append(delim).Append(chunk);
                }
                else
                {
                    yield return current.ToString();
                    current.Clear();
                    current.Append(chunk);
                }
            }
            if (current.Length > 0)
                yield return current.ToString();
        }
    }
}