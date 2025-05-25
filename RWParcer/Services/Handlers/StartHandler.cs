using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers
{
    public class StartHandler(IFacade facade, ICommandRouter router) : ICommandHandler
    {
        private readonly ICommandRouter _router = router;
        private readonly IFacade _facade = facade;

        public async Task HandleAsync(CommandContext ctx)
        {
            await _facade.AuthenticateUser(ctx.ChatId);
            ctx.Session.Reset();
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}