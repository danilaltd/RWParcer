using RWParcer.Converters;
using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Subscriptions
{
    public class SubscriptionsSelectHandler(ICommandRouter router, IFacade facade) : ICommandHandler
    {
        private readonly IFacade _facade = facade;
        private readonly ICommandRouter _router = router;

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await InitSubscriptions(ctx);
                return;
            }

            await HandleTrainSelection(ctx);
        }

        private async Task InitSubscriptions(CommandContext ctx)
        {
            var subscriptions = await _facade.GetSubscritionsAsync(ctx.ChatId, ctx.ChatId);
            if (subscriptions.Count == 0)
            {
                await ctx.ResetSessionAsync("Нет подписок", _router);
                return;
            }

            ctx.Session.Data.Clear();
            ctx.Session.Data.Add(subscriptions);
            await ctx.SendKeyboard(
                subscriptions.Select(t => SubscriptionVOToStringConverter.Convert(t)),
                "Выберите подписку:",
                true);
        }

        private async Task HandleTrainSelection(CommandContext ctx)
        {
            var subscriptionsList = ctx.Session.Data.OfType<List<SubscriptionVO>>().FirstOrDefault();
            if (subscriptionsList == null)
            {
                await ctx.ResetSessionAsync("Сессия устарела, начните заново", _router);
                return;
            }

            if (string.IsNullOrWhiteSpace(ctx.Input))
            {
                await ctx.SendMessage("Выберите поезд из списка клавиатуры");
                return;
            }

            if (!(int.TryParse(ctx.Input, out int index) && index >= 1 && index <= subscriptionsList.Count))
            {
                await ctx.SendMessage("Введите корректный индекс подписки");
                return;
            }

            var selected = subscriptionsList[index - 1];
            ctx.Session.Data.Clear();
            ctx.Session.Data.Add(selected);
            await ctx.SendMessage($"Вы выбрали подписку: {SubscriptionVOToStringConverter.Convert(selected)}");
            ctx.Session.SetCommand(CommandNames.SubscriptionMenuSelect);
            await _router.RouteAsync(CommandNames.SubscriptionMenuSelect, ctx);
        }
    }
}
