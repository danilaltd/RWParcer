using RWParcer.Commands;
using RWParcer.Commands.SubscribeCommands;
using RWParcer.Interfaces;

namespace RWParcer.MenuStates
{
    class SubscribeMenuState : IMenuState
    {
        private readonly List<IMenuCommand> _commands;
        public SubscribeMenuState()
        {
            _commands =
        [
            new ShowAllRoutesCommand(),
            new ShowAllDatesCommand(),
            new ShowRoutesWithDatesCommand(),
            new MainMenuCommand()
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
