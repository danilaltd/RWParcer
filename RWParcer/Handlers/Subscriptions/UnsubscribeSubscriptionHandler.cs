using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Subscriptions
{
    class UnsubscribeSubscriptionHandler : ICommandHandler
    {
        private readonly ICommandRouter _router;
        private readonly IFacade _facade;

        public UnsubscribeSubscriptionHandler(IFacade facade, ICommandRouter router)
        {
            _facade = facade;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            var subscription = ctx.Session.Data.OfType<SubscriptionVO>().First();
            await _facade.UnSubscribeAsync(ctx.ChatId, subscription);
            await ctx.SendMessage($"Отписка выполнена");

            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}
