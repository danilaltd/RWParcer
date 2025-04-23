using RWParcer.NotNow.Interfaces;
using RWParcer.NotNow.MenuStates;

namespace RWParcer.NotNow.Commands
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
