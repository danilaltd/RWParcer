namespace RWParcer.NotNow.Interfaces
{
    public interface IMenuState
    {
        MenuView HandleInput(string input, MenuContext context);
        MenuView GetMenu();
        MenuView GetMenu(string s);
    }

    public interface IMenuStateWithParam<T, V> : IMenuState
    {
        public T? Param { get; }
        MenuView HandleInput(string input, MenuContextRequest<V> context);
    }

}
