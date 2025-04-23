using RWParcer.NotNow.Interfaces;

namespace RWParcer.NotNow.MenuStates.Abstract
{
    public abstract class InputMenuState<T, V> : IMenuStateWithParam<T, V>
    {
        public T? Param { get; protected set; }
        protected abstract string BadInputMsg { get; }
        protected abstract string Header { get; }
        protected virtual MenuView ErrorMessageGetButtons() => new(BadInputMsg + "\n\n" + Header, []);
        public virtual MenuView GetMenu() => new(Header, []);
        public virtual MenuView GetMenu(string s) => new(s + s + "\n\n" + Header, []);
        public virtual MenuView HandleInput(string input, MenuContext context)
        {
            if (context is MenuContextRequest<V> requestContext)
            {
                return HandleInput(input, requestContext);
            }


            if (string.IsNullOrWhiteSpace(input)) return GetMenu();
            return HandleInput_main(input, context);
        }
        public MenuView HandleInput(string input, MenuContextRequest<V> context)
        {
            if (string.IsNullOrWhiteSpace(input)) return GetMenu();
            return HandleInput_main(input, context);
        }
        protected abstract MenuView HandleInput_main(string input, MenuContext context);
        protected abstract MenuView HandleInput_main(string input, MenuContextRequest<V> context);
    }
}
