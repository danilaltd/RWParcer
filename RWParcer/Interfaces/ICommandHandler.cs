namespace RWParcer.Interfaces
{
    public interface ICommandHandler { Task HandleAsync(CommandContext ctx); }
}