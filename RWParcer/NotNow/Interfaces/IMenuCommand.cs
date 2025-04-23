namespace RWParcer.NotNow.Interfaces
{
    public interface IMenuCommand
    {
        string Name { get; }
        void Execute(MenuContext context);
    }
}
