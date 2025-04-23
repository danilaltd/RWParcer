using RWParcer.NotNow.Interfaces;
using RWParcer.NotNow.MenuStates.Search;

namespace RWParcer.NotNow.Commands.MainMenuCommands
{
    public class SearchCommand : IMenuCommand
    {
        public string Name => "Поиск";
        public void Execute(MenuContext context)
        {
            //context.SetState(new SearchMenuState());
            //bool a = context.AddMenuContext<RouteWithTime, EnterStationFromState>();
            //Console.WriteLine(a);
        }
    }
}
