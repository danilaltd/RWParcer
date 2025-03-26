namespace RWParcer.Interfaces
{
    public interface IMenuState
    {
        void DisplayOptions();
        void HandleInput(string input, MenuContext context);
    }
}
