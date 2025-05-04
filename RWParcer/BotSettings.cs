using Telegram.Bot.Types.Enums;

namespace RWParcer
{
    public class BotSettings
    {
        public string ApiToken { get; set; } = string.Empty;
        public string SessionFilePath { get; set; } = "sessions.json";
        public UpdateType[] AllowedUpdates { get; set; } = new[] { UpdateType.Message };
    }

}