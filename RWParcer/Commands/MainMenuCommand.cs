using RWParcer.Interfaces;
using RWParcer.MenuStates;

namespace RWParcer.Commands
{
    public class MainMenuCommand : IMenuCommand
    {
        public string Name => "В главное меню";

        public void Execute(MenuContext context)
        {
            context.SetState(new MainMenuState());
        }
    }
}
