using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.TrainsMenu.Favorites
{
    public class RemoveFromFavoritesHandler(IFacade facade, ICommandRouter router) : ICommandHandler
    {
        private readonly IFacade _facade = facade;
        private readonly ICommandRouter _router = router;

        public async Task HandleAsync(CommandContext ctx)
        {
            var train = ctx.Session.Data.OfType<TrainVO>().FirstOrDefault();
            if (train is null)
            {
                ctx.Session.Reset();
                await ctx.SendMessage("Сессия устарела — начните заново");
                return;
            }

            await _facade.RemoveFromFavoritesAsync(ctx.ChatId, train);
            await ctx.SendMessage("Поезд удален из избранного!");
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }

}