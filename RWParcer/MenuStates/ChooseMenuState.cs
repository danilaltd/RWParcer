using RWParcer.Interfaces;

namespace RWParcer.MenuStates
{
    public abstract class ChooseMenuState : IMenuState
    {
        protected List<IMenuCommand> _commands;
        protected ChooseMenuState(List<IMenuCommand> commands)
        {
            _commands = commands;
        }
        protected abstract string Header { get; }
        protected virtual MenuView ErrorMessageGetButtons() => new("Неверный выбор. Попробуйте снова.\n\n" + Header, [.. _commands.Select(command => command.Name)]);
        public virtual MenuView GetMenu() => new(Header, [.. _commands.Select(command => command.Name)]);
        public virtual MenuView GetMenu(string s) => new(s + "\n\n" + Header, [.. _commands.Select(command => command.Name)]);
        public virtual MenuView HandleInput(string input, MenuContext context)
        {
            if (string.IsNullOrWhiteSpace(input)) return GetMenu();
            IMenuCommand? command = _commands.FirstOrDefault(c => c.Name.Equals(input, StringComparison.CurrentCultureIgnoreCase));
            if (command != null)
            {
                command.Execute(context);
                return context.GetMenu();
            }
            else
            {
                return ErrorMessageGetButtons();
            }
        }
    }
}
