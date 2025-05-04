using RWParcer.Interfaces;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.MenuProviders
{
    public class MainMenuProvider : IMenuProvider
    {
        private readonly IFacade _facade;

        public MainMenuProvider(IFacade facade)
        {
            _facade = facade;
        }

        public async Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>();

            bool isModerator = await _facade.IsUserModeratorAsync(ctx.ChatId, ctx.ChatId);

            if (isModerator)
                options["Меню модератора"] = CommandNames.ModeratorEnterSpan;

            options["🔍 Поиск"] = CommandNames.FromSelect;
            options["⭐ Избранное"] = CommandNames.FavoritesSelect;
            options["⭐ Подписки"] = CommandNames.SubscriptionsSelect;
            options["Мой статус"] = CommandNames.GetStatus;
            options["Обратная связь"] = CommandNames.Feedback;

            return options;
        }
    }
}