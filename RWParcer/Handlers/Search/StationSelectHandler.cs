using RWParcer.Interfaces;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Handlers.Search
{
    public abstract class StationSelectHandler : ICommandHandler
    {
        protected readonly IFacade _facade;
        protected readonly CommandNames _nextCommand;
        protected readonly string _promptText;
        protected readonly string _keyboardText;
        private readonly ICommandRouter _router;

        protected StationSelectHandler(IFacade facade, ICommandRouter router, CommandNames nextCommand, string promptText, string keyboardText)
        {
            _facade = facade;
            _nextCommand = nextCommand;
            _promptText = promptText;
            _keyboardText = keyboardText;
            _router = router;
        }

        public async Task HandleAsync(CommandContext ctx)
        {
            if (ctx.Session.InitState)
            {
                await ctx.SendMessage(_promptText);
                return;
            }

            var existing = ctx.Session.Data.OfType<StationVO>().ToList();

            if (ctx.Session.Data.OfType<List<StationVO>>().FirstOrDefault() is List<StationVO> lastList && lastList.Any(s => s.Label == ctx.Input))
            {
                var chosen = lastList.First(s => s.Label == ctx.Input);
                ctx.Session.Data.Clear();
                ctx.Session.Data.AddRange(existing);
                ctx.Session.Data.Add(chosen);
                ctx.Session.SetCommand(_nextCommand);
                await ctx.SendMessage(string.Format(_keyboardText, chosen.Label));
                await _router.RouteAsync(ctx.Session.CurrentCommand, ctx);
                return;
            }

            var candidates = await _facade.GetStationAsync(ctx.ChatId, ctx.Input);
            if (candidates.Count == 0)
            {
                await ctx.SendMessage($"Станции не найдены. {_promptText}");
                return;
            }

            ctx.Session.Data.RemoveAll(d => d is List<StationVO>);
            ctx.Session.Data.Add(candidates);
            await ctx.SendKeyboard(candidates.Select(s => s.Label), _promptText);
        }
    }
}