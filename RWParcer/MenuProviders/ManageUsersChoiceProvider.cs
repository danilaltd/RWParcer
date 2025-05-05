using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.MenuProviders
{
    public class ManageUsersChoiceProvider : IMenuProvider
    {
        private readonly IFacade _facade;

        public ManageUsersChoiceProvider(IFacade facade)
        {
            _facade = facade;
        }
        public async Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>();
            var user = ctx.Session.Data.OfType<UserVO>().FirstOrDefault() ?? throw new Exception();

            bool isModerator = await _facade.IsUserModeratorAsync(ctx.ChatId, user.Id);
            bool banned = await _facade.IsUserBannedAsync(ctx.ChatId, user.Id);
            if (isModerator)
                options["Понизить до пользователя"] = CommandNames.DemoteUser;
            else
                options["Повысить до модератора"] = CommandNames.PromoteUser;

            if (banned)
                options["Разбанить"] = CommandNames.UnbanUser;
            else
                options["Забанить"] = CommandNames.BanUser;

            options["Изменить максимальное количество подписок"] = CommandNames.ChangeUserMaxSubscribtionLimit;
            options["Изменить минимальный интервал проверки"] = CommandNames.ChangeUserMinIntervalLimit;
            options["Отправить сообщение пользователю"] = CommandNames.SendMessageEnterMessage;
            options["В главное меню"] = CommandNames.MainMenuSelect;

            return options;
        }
    }

}