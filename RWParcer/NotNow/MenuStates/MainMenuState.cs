using RWParcer.NotNow.MenuStates.Abstract;
namespace RWParcer.NotNow.MenuStates
{
    public class MainMenuState : ChooseMenuState
    {
        protected override string Header => "Главное меню";
        public MainMenuState() : base(
        [
            //new SubscribesCommand(),
            //new SearchCommand(),
            //new FavoritesCommand(),
            //new StatusCommand(),
            //new FeedbackCommand(),
            //new ModeratorMenuCommand(),
        ])
        { }
    }
}
