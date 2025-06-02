using RWParcer.Interfaces;
using RWParcer.Services.Commands;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Services.Handlers.TrainsMenu.Subscribe
{
    public class SubscribeUseLastDateHandler(IFacade facade, ICommandRouter router) : ICommandHandler
    {
        private readonly ICommandRouter _router = router;
        private readonly IFacade _facade = facade;

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.Date < DateOnly.FromDateTime(DateTime.Today))
            {
                await ctx.SendMessage("Эта дата уже прошла. Возврат в главное меню");
                ctx.Session.SetCommand(CommandNames.MainMenuSelect);
                await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
                return;
            }

            if (ctx.Session.Date > DateOnly.FromDateTime(DateTime.Today).AddMonths(3))
            {
                await ctx.SendMessage("Эта дата наступит нескоро. Укажите актуальную дату");
                return;
            }


            var train = ctx.Session.Data.OfType<TrainVO>().First();
            try
            {
                await _facade.SubscribeAsync(ctx.ChatId, new SubscriptionVO(train, ctx.Session.Date));
                await ctx.SendMessage($"Подписка установлена на {ctx.Session.Date:dd.MM.yyy}");
            }
            catch (InvalidOperationException)
            {
                await ctx.SendMessage($"Подписка на дату {ctx.Session.Date:dd.MM.yyy} уже существует");
            }
            catch (OverflowException)
            {
                await ctx.SendMessage($"Вы достигли лимита подписок");
            }
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }

}