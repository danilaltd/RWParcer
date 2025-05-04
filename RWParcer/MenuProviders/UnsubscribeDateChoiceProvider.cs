using RWParcer.Interfaces;

namespace RWParcer.MenuProviders
{
    public class UnsubscribeDateChoiceProvider : IMenuProvider
    {
        public Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>
            {
                ["📅 Ввести дату"] = CommandNames.UnsubscribeEnterDate,
                //["🕒 Использовать последнюю"] = CommandNames.UnsubscribeUseLastDate,
                ["В главное меню"] = CommandNames.MainMenuSelect
            };
            return Task.FromResult((IReadOnlyDictionary<string, CommandNames>)options);
        }
    }
}