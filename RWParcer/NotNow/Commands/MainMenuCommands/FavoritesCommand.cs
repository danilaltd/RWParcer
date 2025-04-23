using RWParcer.NotNow.Interfaces;

namespace RWParcer.NotNow.Commands.MainMenuCommands
{
    public class FavoritesCommand : IMenuCommand
    {
        public string Name => "Избранное";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("избр");
            //context.SetState(new HelpMenuState());
        }
    }
}
