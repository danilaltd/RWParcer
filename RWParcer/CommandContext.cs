using RWParcer.Interfaces;
using System.Text;
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

        private async Task SendMessageToClient(string message, ReplyKeyboardMarkup? replyMarkup = null)
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

            // 1) Подбор делимитера
            string chosenDelim = candidateDelimiters.FirstOrDefault(d => message.Contains(d)) ?? " ";
            string delim = chosenDelim ?? "";

            // 2) Разбиваем на блоки по выбранному делимитеру
            List<string> blocks;
            if (chosenDelim != null)
            {
                blocks = message
                    .Split(new[] { chosenDelim }, StringSplitOptions.None)
                    .Select(s => s.Trim())
                    .Where(s => s.Length > 0)
                    .ToList();
            }
            else
            {
                blocks = new List<string> { message };
            }

            // 3) Жёсткое дробление слишком длинных блоков
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

            // 4) Группировка кусков без превышения maxLength
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