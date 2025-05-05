using RWParcer.Interfaces;

namespace RWParcer.MenuProviders
{
    public class SubscribeDateChoiceProvider : IMenuProvider
    {

        public async Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>();

            options["📅 Ввести дату"] = CommandNames.SubscribeEnterDate;
            options[$"🕒 Использовать последнюю дату: {ctx.Session.Date}"] = CommandNames.SubscribeUseLastDate;
            options[$"Ввести диапазон"] = CommandNames.SubscribeEnterDateRange;
            options["В главное меню"] = CommandNames.MainMenuSelect;

            return options;
        }
    }

}