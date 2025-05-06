using RWParcer.Converters;
using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Favorites
{
    public class FavoritesSelectHandler : BaseTrainsHandler
    {
        public FavoritesSelectHandler(ICommandRouter router, IFacade facade) : base(router, facade) { }

        public override async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await InitFavorites(ctx);
                return;
            }

            await HandleTrainSelection(ctx);
        }

        private async Task InitFavorites(CommandContext ctx)
        {
            var favorites = await _facade.GetFavoritesAsync(ctx.ChatId);
            if (favorites.Count == 0)
            {
                await ctx.ResetSessionAsync("В избранном пусто", _router);
                return;
            }

            ctx.Session.Data.Clear();
            ctx.Session.Data.Add(favorites);
            await ctx.SendKeyboard(
                favorites.Select(t => TrainVOToStringConverter.Convert(t)),
                "Выберите элемент:",
                true);
        }
    }
}
