namespace RWParcer.Interfaces
{
    public interface ICommandRouter { 
        Task RouteAsync(CommandNames? cmd, CommandContext ctx); 
    }
}