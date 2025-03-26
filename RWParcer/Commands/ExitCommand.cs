using RWParcer.Interfaces;

namespace RWParcer.Commands
{
    public class ExitCommand : IMenuCommand
    {
        public string Name => "3. Выход";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("Выход из программы.");
            Environment.Exit(0);
        }
    }
}
