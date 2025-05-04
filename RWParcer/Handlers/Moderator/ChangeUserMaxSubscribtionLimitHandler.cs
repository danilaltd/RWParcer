using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Moderator
{
    public class ChangeUserMaxSubscribtionLimitHandler : ICommandHandler
    {
        private readonly IFacade _facade;
        private readonly ICommandRouter _router;

        public ChangeUserMaxSubscribtionLimitHandler(IFacade facade, ICommandRouter router) { 
            _facade = facade;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await ctx.SendMessage("Введите целое неотрицательное число");
                return;
            }

            var user = ctx.Session.Data.OfType<UserVO>().FirstOrDefault();
            if (user is null)
            {
                ctx.Session.Reset();
                await ctx.SendMessage("Сессия устарела — начните заново.");
                return;
            }

            if (!uint.TryParse(ctx.Input, out var num))
            {
                await ctx.SendMessage("Неверный формат, введите целое неотрицательное число.");
                return;
            }

            await _facade.SetUsersMaxSubscriptionsAsync(ctx.ChatId, user.Id, num);
            await ctx.SendMessage("Максимальное число подписок для пользователя установлен");
            ctx.Session.Data.Clear();
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}