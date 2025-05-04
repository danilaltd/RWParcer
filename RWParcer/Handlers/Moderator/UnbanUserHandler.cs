using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Moderator
{
    public class UnbanUserHandler : ICommandHandler
    {
        private readonly IFacade _facade;
        private readonly ICommandRouter _router;

        public UnbanUserHandler(IFacade facade, ICommandRouter router) { 
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

            await _facade.UnbanUserAsync(ctx.ChatId, user.Id);
            await ctx.SendMessage("Пользователь разбанен");
            ctx.Session.Data.Clear();
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}