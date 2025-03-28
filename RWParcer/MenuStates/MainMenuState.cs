using RWParcer.Commands.MainMenuCommands;
namespace RWParcer.MenuStates
{
    public class MainMenuState : ChooseMenuState
    {
        protected override string Header => "Главное меню";
        public MainMenuState() : base(
        [
            new SubscribesCommand(),
            new SearchCommand(),
            new FavoritesCommand(),
            new StatusCommand(),
            new FeedbackCommand(),
            new ModeratorMenuCommand(),
        ])
        { }
    }
}
