using RWParcer.Interfaces;
using RWParcer.Services.Commands;

namespace RWParcer.Services.Menu
{
    public class SubscriptionActionsProvider : IMenuProvider
    {
        public Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>
            {
                ["🚫 Отписаться"] = CommandNames.UnsubscribeSubscription,
                ["Сбросить состояние"] = CommandNames.ResetSubscription,
                ["В главное меню"] = CommandNames.MainMenuSelect
            };

            return Task.FromResult((IReadOnlyDictionary<string, CommandNames>)options);
        }
    }
}