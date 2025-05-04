using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.MenuProviders
{
    public class SubscriptionActionsProvider : IMenuProvider
    {
        private readonly IFacade _facade;

        public SubscriptionActionsProvider(IFacade facade)
        {
            _facade = facade;
        }

        public async Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>
            {
                ["🚫 Отписаться"] = CommandNames.UnsubscribeSubscription,
                ["В главное меню"] = CommandNames.MainMenuSelect
            };

            return options;
        }

    }


}