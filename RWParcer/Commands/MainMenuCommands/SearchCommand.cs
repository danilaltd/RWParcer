using RWParcer.Interfaces;
using RWParcer.MenuStates.Search;

namespace RWParcer.Commands.MainMenuCommands
{
    public class SearchCommand : IMenuCommand
    {
        public string Name => "Поиск";

        public void Execute(MenuContext context)
        {
            context.SetState(new EnterStationFromState());
        }
    }
}
