using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers
{
    public class FeedbackHandler(IFacade facade, ICommandRouter router) : ICommandHandler
    {
        private readonly IFacade _facade = facade;
        private readonly ICommandRouter _router = router;

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await ctx.SendMessage("Введите сообщение");
                return;
            }

            await _facade.SendFeedbackAsync(ctx.ChatId, ctx.Input);
            await ctx.SendMessage("Сообщние отправлено");
            ctx.Session.Data.Clear();
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}