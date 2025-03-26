using RWParcer.Interfaces;

namespace RWParcer.Commands.SubscribeCommands
{
    public class ShowRoutesWithDatesCommand : IMenuCommand
    {
        public string Name => "3. Показать все маршруты с датами и временем";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("Маршруты с датами и временем:");
            // Здесь можно добавить логику для отображения маршрутов с датами и временем
            Console.WriteLine("Маршрут 1: Минск - Брест, дата: 01.05.2025, время: 10:00");
            Console.WriteLine("Маршрут 2: Минск - Гродно, дата: 15.05.2025, время: 12:30");
            Console.WriteLine("Маршрут 3: Минск - Витебск, дата: 30.05.2025, время: 08:45");
        }
    }


}
