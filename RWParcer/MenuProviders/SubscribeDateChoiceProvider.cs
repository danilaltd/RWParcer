using RWParcer.Interfaces;

namespace RWParcer.MenuProviders
{
    public class SubscribeDateChoiceProvider : IMenuProvider
    {
        public Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>
            {
                ["📅 Ввести дату"] = CommandNames.SubscribeEnterDate,
                //["🕒 Использовать последнюю"] = CommandNames.SubscribeUseLastDate,
                ["В главное меню"] = CommandNames.MainMenuSelect
            };
            return Task.FromResult((IReadOnlyDictionary<string, CommandNames>)options);
        }
    }

}