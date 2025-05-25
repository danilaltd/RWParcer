using RWParcer.Interfaces;
using RWParcer.Services.Commands;

namespace RWParcer.Services.Menu
{
    public class SubscribeDateChoiceProvider : IMenuProvider
    {
        public Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>();

            options["📅 Ввести дату"] = CommandNames.SubscribeEnterDate;
            options[$"🕒 Использовать последнюю дату: {ctx.Session.Date}"] = CommandNames.SubscribeUseLastDate;
            options[$"Ввести диапазон"] = CommandNames.SubscribeEnterDateRange;
            options["В главное меню"] = CommandNames.MainMenuSelect;

            return Task.FromResult((IReadOnlyDictionary<string, CommandNames>)options);
        }
    }
}