namespace RWParcer.Interfaces
{
    public interface IMenuCommand
    {
        string Name { get; } // Имя команды, отображаемое в меню
        void Execute(MenuContext context); // Логика выполнения команды
    }
}
