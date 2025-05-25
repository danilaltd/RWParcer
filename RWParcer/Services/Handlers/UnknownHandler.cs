using RWParcer.Interfaces;
using RWParcer.Services.Commands;

namespace RWParcer.Services.Handlers
{
    public class UnknownHandler : ICommandHandler
    {
        public Task HandleAsync(CommandContext ctx) => ctx.SendMessage("Неизвестная команда. Используйте /start");
    }
}