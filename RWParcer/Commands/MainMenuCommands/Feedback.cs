using RWParcer.Interfaces;

namespace RWParcer.Commands.MainMenuCommands
{
    public class Feedback : IMenuCommand
    {
        public string Name => "Показать все подписки";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("меню подписок");
            //context.SetState(new HelpMenuState());
        }
    }
}
