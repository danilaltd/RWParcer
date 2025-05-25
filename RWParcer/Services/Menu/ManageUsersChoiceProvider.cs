using RWParcer.Interfaces;
using RWParcer.Services.Commands;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Services.Menu
{
    public class ManageUsersChoiceProvider(IFacade facade) : IMenuProvider
    {
        private readonly IFacade _facade = facade;

        public async Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>();
            var user = ctx.Session.Data.OfType<UserVO>().FirstOrDefault() ?? throw new Exception();

            bool isModerator = await _facade.IsUserModeratorAsync(ctx.ChatId, user.Id);
            bool banned = await _facade.IsUserBannedAsync(ctx.ChatId, user.Id);
            if (isModerator)
                options["⬇️ Понизить до пользователя"] = CommandNames.DemoteUser;
            else
                options["⬆️ Повысить до модератора"] = CommandNames.PromoteUser;

            if (banned)
                options["✅ Разбанить"] = CommandNames.UnbanUser;
            else
                options["🚫 Забанить"] = CommandNames.BanUser;

            options["📊 Лимит подписок"] = CommandNames.ChangeUserMaxSubscribtionLimit;
            options["⏱️ Интервал проверки"] = CommandNames.ChangeUserMinIntervalLimit;
            options["✉️ Отправить сообщение"] = CommandNames.SendMessageEnterMessage;
            options["🏠 В главное меню"] = CommandNames.MainMenuSelect;

            return options;
        }
    }

}