using RWParcer.Interfaces;

namespace RWParcer.Handlers
{
    public class UnknownHandler : ICommandHandler
    {
        public Task HandleAsync(CommandContext ctx) => ctx.SendMessage("Неизвестная команда. Используйте /start.");
    }
}