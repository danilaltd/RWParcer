using RWParcer.Commands;
using RWParcer.Commands.MainMenuCommands;
using RWParcer.Commands.SubscribeCommands;
using RWParcer.Interfaces;

namespace RWParcer.MenuStates.MainMenuStates
{
    class FavoritesMenuState : ChooseMenuState
    {
        protected override string Header => "Избранное";
        public FavoritesMenuState() : base(
        [
            //new SubscribeCommand(),
            //new UnsubscribeCommand(),
            new ShowRoutesWithDatesCommand(),
            new MainMenuCommand()
        ])
        { }
    }
}
