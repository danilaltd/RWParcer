using RWParcer.Interfaces;

namespace RWParcer.MenuStates
{
    public abstract class InputMenuState : IMenuState
    {
        protected abstract string BadInputMsg { get; }
        protected abstract string Header { get; }
        protected virtual MenuView ErrorMessageGetButtons() => new(BadInputMsg + "\n\n" + Header, []);
        public virtual MenuView GetMenu() => new(Header, []);
        public virtual MenuView GetMenu(string s) => new(s + s + "\n\n" + Header, []);
        public virtual MenuView HandleInput(string input, MenuContext context)
        {
            if (string.IsNullOrWhiteSpace(input)) return GetMenu();
            return HandleInput_main(input, context);
        }
        protected abstract MenuView HandleInput_main(string input, MenuContext context);
    }
}
