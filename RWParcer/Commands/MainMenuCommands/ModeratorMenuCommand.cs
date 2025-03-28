using RWParcer.Interfaces;

namespace RWParcer.Commands.MainMenuCommands
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
