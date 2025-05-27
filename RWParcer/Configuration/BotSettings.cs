using Telegram.Bot.Types.Enums;

namespace RWParcer.Configuration
{
    public class BotSettings
    {
        public string ApiToken { get; set; } = string.Empty;
        public string SessionFilePath { get; set; } = "sessions.json";
        public string SessionDbConnectionString { get; set; } = "Data Source=sessions.db";
        public UpdateType[] AllowedUpdates { get; set; } = [UpdateType.Message];
    }

}