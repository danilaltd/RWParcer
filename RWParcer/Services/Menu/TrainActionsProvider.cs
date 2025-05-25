using RWParcer.Interfaces;
using RWParcer.Services.Commands;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Services.Menu
{
    public class TrainActionsProvider(IFacade facade) : IMenuProvider
    {
        private readonly IFacade _facade = facade;

        public async Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>();

            var train = ctx.Session.Data.OfType<TrainVO>().FirstOrDefault() ?? throw new Exception();
            bool isFavorite = await _facade.IsInFavoritesAsync(ctx.ChatId, train);

            if (!isFavorite)
                options["⭐ Добавить в избранное"] = CommandNames.AddToFavorites;
            else
                options["⭐ Удалить из избранного"] = CommandNames.RemoveFromFavorites;


            options["🔔 Подписаться"] = CommandNames.SubscribeDateSelect;
            options["🚫 Отписаться"] = CommandNames.UnsubscribeDateSelect;
            options["В главное меню"] = CommandNames.MainMenuSelect;

            return options;
        }

    }


}