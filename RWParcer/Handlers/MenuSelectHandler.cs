using RWParcer.Interfaces;

namespace RWParcer.Handlers
{
    public class MenuSelectHandler(
        ICommandRouter router,
        IMenuProvider menu,
        string menuHead) : ICommandHandler
    {
        private readonly ICommandRouter _router = router;
        private readonly IMenuProvider _menu = menu;
        private readonly string MenuHead = menuHead;

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await ctx.SendKeyboard(
                    (await _menu.GetOptionsAsync(ctx)).Keys,
                    MenuHead);
                return;
            }

            if ((await _menu.GetOptionsAsync(ctx)).TryGetValue(ctx.Input, out var nextCommand))
            {
                ctx.Session.SetCommand(nextCommand);
                await _router.RouteAsync(nextCommand, ctx);
            }
            else
            {
                await ctx.SendKeyboard(
                    (await _menu.GetOptionsAsync(ctx)).Keys,
                    "Неверный ввод. Пожалуйста, выберите пункт из меню:");
            }
        }
    }

}