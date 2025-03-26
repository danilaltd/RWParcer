using RWParcer.Commands.MainMenuCommands;
using RWParcer.Interfaces;

namespace RWParcer.MenuStates
{
    class MainMenuState : IMenuState
    {
        private readonly List<IMenuCommand> _commands;

        public MainMenuState()
        {
            _commands =
        [
            new Subscribes(),
            new Search(),
            new Favorites(),
            new Status(),
            new Feedback(),
            new ModeratorMenu(),
        ];
        }

        public void DisplayOptions()
        {
            foreach (var command in _commands)
            {
                Console.WriteLine(command.Name);
            }
        }

        public void HandleInput(string input, MenuContext context)
        {
            var command = _commands.FirstOrDefault(c => c.Name.ToLower().StartsWith(input.ToLower()));
            if (command != null)
            {
                command.Execute(context);
            }
            else
            {
                Console.WriteLine("Неверный выбор. Попробуйте снова.");
            }
        }
    }
}
