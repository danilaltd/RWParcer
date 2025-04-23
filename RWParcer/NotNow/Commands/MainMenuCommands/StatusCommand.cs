using RWParcer.NotNow.Interfaces;

namespace RWParcer.NotNow.Commands.MainMenuCommands
{
    public class StatusCommand : IMenuCommand
    {
        public string Name => "Статус";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("статус");
            //context.SetState(new HelpMenuState());
        }
    }
}
