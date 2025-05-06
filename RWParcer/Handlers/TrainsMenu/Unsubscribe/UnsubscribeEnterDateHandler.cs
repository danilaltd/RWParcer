using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.TrainsMenu.Unsubscribe
{
    public class UnsubscribeEnterDateHandler : ICommandHandler
    {
        private readonly ICommandRouter _router;
        private readonly IFacade _facade;

        public UnsubscribeEnterDateHandler(IFacade facade, ICommandRouter router)
        {
            _facade = facade;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await ctx.SendMessage("Введите дату в формате DD.MM.YYYY");
                return;
            }

            if (!DateOnly.TryParseExact(ctx.Input, "dd.MM.yyyy", out var date))
            {
                await ctx.SendMessage("Неверный формат даты, используйте DD.MM.YYYY");
                return;
            }

            var train = ctx.Session.Data.OfType<TrainVO>().First();
            ctx.Session.Date = date;

            try
            {
                await _facade.UnSubscribeAsync(ctx.ChatId, new SubscriptionVO(train, date));
                await ctx.SendMessage($"Отписка выполнена на {date:dd.MM.yyyy}");
            }
            catch (InvalidOperationException)
            {
                await ctx.SendMessage($"Подписка на дату {date:dd.MM.yyy} не существует");
            }
            
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}