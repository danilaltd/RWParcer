using RWParcer.Interfaces;
using RWParcer.Services.Commands;

namespace RWParcer.Services.Menu
{
    public class UnsubscribeDateChoiceProvider : IMenuProvider
    {
        public Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>();

            options["📅 Ввести дату"] = CommandNames.UnsubscribeEnterDate;
            options[$"🕒 Использовать последнюю дату: {ctx.Session.Date}"] = CommandNames.UnsubscribeUseLastDate;
            options[$"Ввести диапазон"] = CommandNames.UnsubscribeEnterDateRange;
            options["🏠 В главное меню"] = CommandNames.MainMenuSelect;

            return Task.FromResult((IReadOnlyDictionary<string, CommandNames>)options);
        }
    }
}