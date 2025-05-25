using RWParcer.Interfaces;
using RWParcer.Services.Commands;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Services.Menu
{
    public class MainMenuProvider(IFacade facade) : IMenuProvider
    {
        private readonly IFacade _facade = facade;

        public async Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>();

            bool isModerator = await _facade.IsUserModeratorAsync(ctx.ChatId, ctx.ChatId);



            options["🔍 Поиск"] = CommandNames.FromSelect;
            options["⭐ Избранное"] = CommandNames.FavoritesSelect;
            options["⭐ Подписки"] = CommandNames.SubscriptionsSelect;
            options["Мой статус"] = CommandNames.GetStatus;
            if (isModerator)
                options["Меню модератора"] = CommandNames.ModeratorMenuSelect;
            options["Просмотреть сообщения"] = CommandNames.ViewMessages;
            options["Обратная связь"] = CommandNames.Feedback;

            return options;
        }
    }
}