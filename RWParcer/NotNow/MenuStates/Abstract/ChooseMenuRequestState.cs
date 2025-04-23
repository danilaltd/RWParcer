using RWParcer.NotNow.Interfaces;

namespace RWParcer.NotNow.MenuStates.Abstract
{
    public abstract class ChooseMenuRequestState<T> : IMenuState
    {
        public MenuContextRequest<T>? MenuRequest { get; set; }
        protected List<IMenuCommand> _commands;
        protected ChooseMenuRequestState(List<IMenuCommand> commands)
        {
            _commands = commands;
        }
        protected abstract string Header { get; }
        protected virtual MenuView ErrorMessageGetButtons() => new("Неверный выбор. Попробуйте снова.\n\n" + Header, [.. _commands.Select(command => command.Name)]);
        public virtual MenuView GetMenu() => new(Header, [.. _commands.Select(command => command.Name)]);
        public virtual MenuView GetMenu(string s) => new(s + "\n\n" + Header, [.. _commands.Select(command => command.Name)]);
        public virtual MenuView HandleInput(string input, MenuContext context)
        {
            if (MenuRequest != null && !MenuRequest.done)
            {
                MenuView proc = MenuRequest.HandleInput(input);
                if (!MenuRequest.done)
                    return proc;
                return GetMenu();
            }
            if (MenuRequest != null)
            {
                MenuRequest = null;
            }
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
