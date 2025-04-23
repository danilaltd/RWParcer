using RWParcer.NotNow.Interfaces;

namespace RWParcer.NotNow.Commands.MainMenuCommands
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
