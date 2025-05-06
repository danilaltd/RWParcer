using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Moderator
{
    public class SendMessageEnterMessageHandler : ICommandHandler
    {
        private readonly IFacade _facade;
        private readonly ICommandRouter _router;

        public SendMessageEnterMessageHandler(IFacade facade, ICommandRouter router)
        {
            _facade = facade;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await ctx.SendMessage("Введите сообщение");
                return;
            }

            var user = ctx.Session.Data.OfType<UserVO>().FirstOrDefault();
            if (user is null)
            {
                ctx.Session.Reset();
                await ctx.SendMessage("Сессия устарела — начните заново");
                return;
            }

            await _facade.SendMessageAsync(ctx.ChatId, user.Id, ctx.Input);
            await ctx.SendMessage("Сообщение отправлено");

            ctx.Session.Data.Clear();
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}
