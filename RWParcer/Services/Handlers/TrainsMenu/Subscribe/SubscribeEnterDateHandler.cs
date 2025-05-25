using RWParcer.Interfaces;
using RWParcer.Services.Commands;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Services.Handlers.TrainsMenu.Subscribe
{
    public class SubscribeEnterDateHandler(IFacade facade, ICommandRouter router) : ICommandHandler
    {
        private readonly ICommandRouter _router = router;
        private readonly IFacade _facade = facade;

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

            if (date < DateOnly.FromDateTime(DateTime.Today))
            {
                await ctx.SendMessage("Эта дата уже прошла. Укажите актуальную дату");
                return;
            }

            if (date > DateOnly.FromDateTime(DateTime.Today).AddMonths(3))
            {
                await ctx.SendMessage("Эта дата наступит нескоро. Укажите актуальную дату");
                return;
            }

            var train = ctx.Session.Data.OfType<TrainVO>().First();
            ctx.Session.Date = date;
            try
            {
                await _facade.SubscribeAsync(ctx.ChatId, new SubscriptionVO(train, date));
                await ctx.SendMessage($"Подписка установлена на {date:dd.MM.yyy}");
            }
            catch (InvalidOperationException)
            {
                await ctx.SendMessage($"Подписка на дату {date:dd.MM.yyy} уже существует");
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