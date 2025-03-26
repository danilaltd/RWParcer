using RWParcer.Interfaces;

namespace RWParcer.Commands.MainMenuCommands
{
    public class Status : IMenuCommand
    {
        public string Name => "Статус";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("статус");
            //context.SetState(new HelpMenuState());
        }
    }
}
