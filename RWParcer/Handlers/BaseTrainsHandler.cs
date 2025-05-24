using RWParcer.Converters;
using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers
{
    public abstract class BaseTrainsHandler(ICommandRouter router, IFacade facade) : ICommandHandler
    {
        protected readonly IFacade _facade = facade;
        protected readonly ICommandRouter _router = router;

        public abstract Task HandleAsync(CommandContext ctx);

        protected async Task HandleTrainSelection(CommandContext ctx)
        {
            var trainsList = ctx.Session.Data.OfType<List<TrainVO>>().FirstOrDefault();
            if (trainsList == null)
            {
                await ctx.ResetSessionAsync("Сессия устарела, начните заново", _router);
                return;
            }

            if (string.IsNullOrWhiteSpace(ctx.Input))
            {
                await ctx.SendMessage("Выберите поезд из списка клавиатуры");
                return;
            }

            if (!(int.TryParse(ctx.Input, out int index) && index >= 1 && index <= trainsList.Count))
            {
                await ctx.SendMessage("Введите корректный индекс поезда");
                return;
            }

            var selected = trainsList[index - 1];
            ctx.Session.Data.Clear();
            ctx.Session.Data.Add(selected);
            await ctx.SendMessage($"Вы выбрали поезд: {TrainVOToStringConverter.Convert(selected)}");
            ctx.Session.SetCommand(CommandNames.TrainMenuSelect);
            await _router.RouteAsync(CommandNames.TrainMenuSelect, ctx);
        }
    }

}