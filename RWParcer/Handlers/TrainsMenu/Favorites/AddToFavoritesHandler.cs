using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.TrainsMenu.Favorites
{
    public class AddToFavoritesHandler : ICommandHandler
    {
        private readonly IFacade _facade;
        private readonly ICommandRouter _router;

        public AddToFavoritesHandler(IFacade facade, ICommandRouter router) { 
            _facade = facade;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            var train = ctx.Session.Data.OfType<TrainVO>().FirstOrDefault();
            if (train is null)
            {
                ctx.Session.Reset();
                await ctx.SendMessage("Сессия устарела — начните заново.");
                return;
            }

            await _facade.AddToFavoritesAsync(ctx.ChatId, train);
            await ctx.SendMessage("Поезд добавлен в избранное!");
            ctx.Session.SetCommand(CommandNames.MainMenuSelect);
            await _router.RouteAsync(CommandNames.MainMenuSelect, ctx);
        }
    }

}