using RWParcer.Converters;
using RWParcer.Interfaces;
using RWParcer.Services.Commands;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Services.Handlers.Search
{
    public class TrainSearchSelectHandler(ICommandRouter router, IFacade facade) : BaseTrainsHandler(router, facade)
    {
        public override async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await InitRoutes(ctx);
                return;
            }

            await HandleTrainSelection(ctx);
        }

        private async Task InitRoutes(CommandContext ctx)
        {
            var stations = ctx.Session.Data.OfType<StationVO>().ToList();
            if (stations.Count != 2)
            {
                await ctx.ResetSessionAsync("Ошибка выбора станции. Начните заново", _router);
                return;
            }

            var trains = await _facade.GetTimesForRouteAsync(ctx.ChatId, new RouteVO(stations[0], stations[1]));
            if (trains.Count == 0)
            {
                await ctx.ResetSessionAsync("Поезда не найдены", _router);
                return;
            }

            ctx.Session.Data.Clear();
            ctx.Session.Data.Add(trains);
            await ctx.SendKeyboard(
                trains.Select(t => TrainVOToStringConverter.Convert(t)),
                "Выберите поезд:",
                true);
        }
    }

}