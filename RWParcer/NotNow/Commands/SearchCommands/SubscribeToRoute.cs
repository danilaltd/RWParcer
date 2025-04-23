using RWParcer.NotNow.Interfaces;

namespace RWParcer.NotNow.Commands.SearchCommands
{
    public class SubscribeToRoute : IMenuCommand
    {
        //private RouteWithTime route;
        //public SubscribeToRoute(RouteWithTime r) {
            //route = r;
        //}
        public string Name => "Подписаться на маршрут";

        public void Execute(MenuContext context)
        {
            //context.SetState(new EnterStationFromState());
        }
    }


}
