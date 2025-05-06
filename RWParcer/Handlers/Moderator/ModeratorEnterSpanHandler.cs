using RWParcer.Interfaces;

namespace RWParcer.Handlers.Moderator
{
    public class ModeratorEnterSpanHandler : ICommandHandler
    {
        private readonly ICommandRouter _router;

        public ModeratorEnterSpanHandler(ICommandRouter router)
        {
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                string ans = "Введите промежуток времени в формате d*.hh:mm:ss";
                await ctx.SendMessage(ans);
                return;
            }

            if (!TimeSpan.TryParse(ctx.Input, out var ts) || ts == default)
            {
                await ctx.SendMessage("Неверный формат времени, используйте d*.hh:mm:ss");
                return;
            }

            ctx.Session.Data.Add(ts);
            ctx.Session.SetCommand(CommandNames.SelectUser);
            await _router.RouteAsync(CommandNames.SelectUser, ctx);
        }
    }

}