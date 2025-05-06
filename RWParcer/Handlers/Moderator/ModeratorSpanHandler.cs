using RWParcer.Interfaces;

namespace RWParcer.Handlers.Moderator
{
    public class ModeratorSpanHandler : ICommandHandler
    {
        private readonly ICommandRouter _router;
        private readonly TimeSpan _span;

        public ModeratorSpanHandler(ICommandRouter router, TimeSpan span)
        {
            _router = router;
            _span = span;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            ctx.Session.Data.Add(_span);
            ctx.Session.SetCommand(CommandNames.SelectUser);
            await _router.RouteAsync(CommandNames.SelectUser, ctx);
        }
    }
}