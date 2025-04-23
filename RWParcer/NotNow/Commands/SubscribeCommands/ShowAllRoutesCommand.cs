using RWParcer.NotNow.Interfaces;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RWParcer.NotNow.Commands.SubscribeCommands
{
    public class ShowAllRoutesCommand : IMenuCommand
    {
        public string Name => "1. Показать все маршруты";

        public void Execute(MenuContext context)
        {
            Console.WriteLine("Все доступные маршруты:");
            // Здесь можно добавить логику для отображения маршрутов
            Console.WriteLine("Маршрут 1: Минск - Брест");
            Console.WriteLine("Маршрут 2: Минск - Гродно");
            Console.WriteLine("Маршрут 3: Минск - Витебск");
        }
    }


}
