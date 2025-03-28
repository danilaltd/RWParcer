namespace RWParcer.Interfaces
{
    public interface IMenuState
    {
        MenuView HandleInput(string input, MenuContext context);
        MenuView GetMenu();
        MenuView GetMenu(string s);
    }
}
