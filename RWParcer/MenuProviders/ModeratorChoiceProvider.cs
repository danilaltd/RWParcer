using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcer.MenuProviders
{
    public class ModeratorChoiceProvider : IMenuProvider
    {
        public Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>
            {
                ["Получить пользователей за промежуток времени"] = CommandNames.ModeratorEnterSpan,
                ["Просмотреть все сообщения"] = CommandNames.ViewAllMessages,
            };
            return Task.FromResult((IReadOnlyDictionary<string, CommandNames>)options);
        }
    }

}