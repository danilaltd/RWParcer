using RWParcer.Commands.SubscribeCommands;
namespace RWParcer.MenuStates
{
    public class SearchMenuState : ChooseMenuState
    {
        protected override string Header => "Главное меню";
        private RouteWithTime rote;
        public SearchMenuState(RouteWithTime r) : base(
        [
            new SubscribeToRoute(r),
        ])
        { }
    }
}
