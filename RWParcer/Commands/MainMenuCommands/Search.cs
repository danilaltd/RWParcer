using RWParcer.Interfaces;

namespace RWParcer.Commands.MainMenuCommands
{
    public class Search : IMenuCommand
    {
        public string Name => "Поиск";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("поиск");
            //context.SetState(new HelpMenuState());
        }
    }
}
