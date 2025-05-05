using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.TrainsMenu.Unsubscribe
{
    public class UnsubscribeUseLastDateHandler : ICommandHandler
    {
        private readonly ICommandRouter _router;
        private readonly IFacade _facade;

        public UnsubscribeUseLastDateHandler(IFacade facade, ICommandRouter router)
        {
            _facade = facade;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            var train = ctx.Session.Data.OfType<TrainVO>().First();
            try
            {
                await _facade.UnSubscribeAsync(ctx.ChatId, new SubscriptionVO(train, ctx.Session.Date));
                await ctx.SendMessage($"Отписка выполнена на {ctx.Session.Date:dd.MM.yyyy}");
            }
            catch (InvalidOperationException)
            {
                await ctx.SendMessage($"Подписка на дату {ctx.Session.Date:dd.MM.yyy} не существует");
            }
            
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}