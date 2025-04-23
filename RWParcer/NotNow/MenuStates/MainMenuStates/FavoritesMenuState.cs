using RWParcer.NotNow.MenuStates.Abstract;

namespace RWParcer.NotNow.MenuStates.MainMenuStates
{
    class FavoritesMenuState : ChooseMenuState
    {
        protected override string Header => "Избранное";
        public FavoritesMenuState() : base(
        [
            //new SubscribeCommand(),
            //new UnsubscribeCommand(),
            //new ShowRoutesWithDatesCommand(),
            //new MainMenuCommand()
        ])
        { }
    }
}
