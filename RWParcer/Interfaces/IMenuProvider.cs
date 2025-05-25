using RWParcer.Services.Commands;

namespace RWParcer.Interfaces
{
    public interface IMenuProvider
    {
        Task<IReadOnlyDictionary<string, CommandNames>> GetOptionsAsync(CommandContext ctx);
    }
}