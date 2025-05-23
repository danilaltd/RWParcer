using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers
{
    public class StartHandler : ICommandHandler
    {
        private readonly ICommandRouter _router;
        private readonly IFacade _facade;

        public StartHandler(IFacade facade, ICommandRouter router)
        {
            _facade = facade;
            _router = router;
        }
        public async Task HandleAsync(CommandContext ctx)
        {
            await _facade.AuthenticateUser(ctx.ChatId);
            ctx.Session.Reset();
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}