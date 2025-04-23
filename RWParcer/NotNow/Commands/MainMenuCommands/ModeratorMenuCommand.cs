using RWParcer.NotNow.Interfaces;

namespace RWParcer.NotNow.Commands.MainMenuCommands
{
    public class ModeratorMenuCommand : IMenuCommand
    {
        public string Name => "Меню Модератора";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("модер");
            //context.SetState(new HelpMenuState());
        }
    }
}
