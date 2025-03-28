using RWParcer.Interfaces;
using RWParcer.MenuStates.MainMenuStates;

namespace RWParcer.Commands.MainMenuCommands
{
    public class SubscribesCommand : IMenuCommand
    {
        public string Name => "Показать все подписки";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("меню подписок");
            context.SetState(new SubscribeMenuState());
        }
    }
}
