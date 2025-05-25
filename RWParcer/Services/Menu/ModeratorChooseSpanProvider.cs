using RWParcer.Interfaces;
using RWParcer.Services.Commands;

namespace RWParcer.Services.Menu
{
    public class ModeratorChooseSpanProvider : IMenuProvider
    {
        public Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx)
        {
            var options = new Dictionary<string, CommandNames>
            {
                ["📅 Ввести период"] = CommandNames.ModeratorEnterSpan,
                ["⏱️ Последняя минута"] = CommandNames.ModeratorSpanMinute,
                ["🕐 Последний час"] = CommandNames.ModeratorSpanHour,
                ["📆 Последний день"] = CommandNames.ModeratorSpanDay,
            };
            return Task.FromResult((IReadOnlyDictionary<string, CommandNames>)options);
        }
    }

}