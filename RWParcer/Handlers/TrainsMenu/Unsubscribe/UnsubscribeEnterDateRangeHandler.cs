using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace RWParcer.Handlers.TrainsMenu.Unsubscribe
{
    public class UnsubscribeEnterDateRangeHandler : ICommandHandler
    {
        private readonly ICommandRouter _router;
        private readonly IFacade _facade;

        public UnsubscribeEnterDateRangeHandler(IFacade facade, ICommandRouter router)
        {
            _facade = facade;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await ctx.SendMessage("Введите диапазон в формате DD.MM.YYYY-DD.MM.YYYY");
                return;
            }

            var dates = ctx.Input.Split('-');

            if (dates.Length != 2 ||
                !DateOnly.TryParseExact(dates[0].Trim(), "dd.MM.yyyy", out var startDate) ||
                !DateOnly.TryParseExact(dates[1].Trim(), "dd.MM.yyyy", out var endDate) ||
                startDate > endDate)
            {
                await ctx.SendMessage("Неверный формат диапазона, используйте DD.MM.YYYY-DD.MM.YYYY");
                return;
            }

            if ((endDate.DayNumber - startDate.DayNumber) >= 60)
            {
                await ctx.SendMessage("Слишком большой диапазон");
                return;
            }

            if (startDate < DateOnly.FromDateTime(DateTime.Today))
            {
                await ctx.SendMessage("Эта дата уже прошла. Укажите актуальную дату");
                return;
            }

            if (endDate > DateOnly.FromDateTime(DateTime.Today).AddMonths(3))
            {
                await ctx.SendMessage("Эта дата наступит нескоро. Укажите актуальную дату");
                return;
            }

            var train = ctx.Session.Data.OfType<TrainVO>().First();
            string ans = "";

            for (var date = startDate; date <= endDate; date = date.AddDays(1))
            {
                try
                {
                    await _facade.UnSubscribeAsync(ctx.ChatId, new SubscriptionVO(train, date));
                }
                catch (InvalidOperationException)
                {
                    ans += $"Подписка на дату {date:dd.MM.yyyy} не существует\n";
                }
            }
            await ctx.SendMessage($"Отписка выполнена на {startDate:dd.MM.yyyy} - {endDate:dd.MM.yyyy}" + (string.IsNullOrEmpty(ans) ? "" : ("\n" + ans)));

            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}