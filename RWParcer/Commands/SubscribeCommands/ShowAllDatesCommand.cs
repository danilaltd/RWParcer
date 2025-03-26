using RWParcer.Interfaces;

namespace RWParcer.Commands.SubscribeCommands
{
    public class ShowAllDatesCommand : IMenuCommand
    {
        public string Name => "2. Показать все даты";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("Все доступные даты:");
            // Здесь можно добавить логику для отображения дат
            Console.WriteLine("Дата 1: 01.05.2025");
            Console.WriteLine("Дата 2: 15.05.2025");
            Console.WriteLine("Дата 3: 30.05.2025");
        }
    }


}
