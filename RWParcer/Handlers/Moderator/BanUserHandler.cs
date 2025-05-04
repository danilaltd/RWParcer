using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Moderator
{
    public class BanUserHandler : ICommandHandler
    {
        private readonly IFacade _facade;
        private readonly ICommandRouter _router;

        public BanUserHandler(IFacade facade, ICommandRouter router) { 
            _facade = facade;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            var user = ctx.Session.Data.OfType<UserVO>().FirstOrDefault();
            if (user is null)
            {
                ctx.Session.Reset();
                await ctx.SendMessage("Сессия устарела — начните заново.");
                return;
            }

            await _facade.BanUserAsync(ctx.ChatId, user.Id);
            await ctx.SendMessage("Пользователь забанен");
            ctx.Session.Data.Clear();
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}