namespace RWParcer.Interfaces
{
    public interface IMenuCommand
    {
        string Name { get; }
        void Execute(MenuContext context);
    }
}
