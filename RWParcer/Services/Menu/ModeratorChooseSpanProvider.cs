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
                ["Ввести промежуток времени"] = CommandNames.ModeratorEnterSpan,
                ["За последнюю минуту"] = CommandNames.ModeratorSpanMinute,
                ["За последний час"] = CommandNames.ModeratorSpanHour,
                ["За последний день"] = CommandNames.ModeratorSpanDay,
            };
            return Task.FromResult((IReadOnlyDictionary<string, CommandNames>)options);
        }
    }

}