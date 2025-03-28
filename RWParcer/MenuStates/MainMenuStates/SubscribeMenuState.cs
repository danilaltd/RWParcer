using RWParcer.Commands;
using RWParcer.Commands.SubscribeCommands;

namespace RWParcer.MenuStates.MainMenuStates
{
    class SubscribeMenuState : ChooseMenuState
    {
        protected override string Header => "Показать все подписки";
        public SubscribeMenuState() : base(
        [
            //new ShowAllRoutesCommand(),
            //new SubscribeToRoute(),
            //new ShowRoutesWithDatesCommand(),
            //new MainMenuCommand()
        ])
        { }
    }
}
