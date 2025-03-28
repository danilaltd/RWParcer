using RWParcer.Interfaces;

namespace RWParcer.Commands.MainMenuCommands
{
    public class FeedbackCommand : IMenuCommand
    {
        public string Name => "Обратная связь";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("Обр связь");
        }
    }
}
