using RWParcer.Interfaces;

namespace RWParcer.Handlers.Moderator
{
    public class ModeratorSpanHandler(ICommandRouter router, TimeSpan span) : ICommandHandler
    {
        private readonly ICommandRouter _router = router;
        private readonly TimeSpan _span = span;

        public async Task HandleAsync(CommandContext ctx)
        {
            ctx.Session.Data.Add(_span);
            ctx.Session.SetCommand(CommandNames.SelectUser);
            await _router.RouteAsync(CommandNames.SelectUser, ctx);
        }
    }
}