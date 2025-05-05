using RWParcer.Converters;
using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Moderator
{
    public class ViewAllMessagesHandler : ICommandHandler
    {
        private readonly IFacade _facade;
        private readonly ICommandRouter _router;

        public ViewAllMessagesHandler(IFacade facade, ICommandRouter router) { 
            _facade = facade;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            var messages = await _facade.GetAllMessagesAsync(ctx.ChatId);
            if (messages.Count > 0) {
                string text = "Все сообщения:\n\n";
                text += string.Join("\n\n", (messages).Select(m => MessageVOToStringConverter.Convert(m)));
                await ctx.SendMessage(text);
            } else
            {
                await ctx.SendMessage("Нет сообщений");
            }
            ctx.Session.Data.Clear();
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }
}