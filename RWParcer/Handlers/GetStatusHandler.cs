using RWParcer.Converters;
using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers
{
    public class GetStatusHandler : ICommandHandler
    {
        private readonly IFacade _facade;
        private readonly ICommandRouter _router;

        public GetStatusHandler(IFacade facade, ICommandRouter router)
        {
            _facade = facade;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            var user = await _facade.GetUserByIdAsync(ctx.ChatId, ctx.ChatId);
            await ctx.SendMessage("Ваш статус: " + UserVOToStringConverter.Convert(user));
            ctx.Session.Data.Clear();
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }

}