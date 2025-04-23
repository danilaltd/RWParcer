using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

class Program
{
    static async Task Main()
    {
        string user1 = "12345";
        string user2 = "12346";

        Facade facade = await Facade.CreateAsync();
        facade.AuthenticateUser(user1);
        facade.AuthenticateUser(user2);
        while (true)
        {
            try
            {
                await CheckNotificationsLoopAsync(facade);

                //StationVO fromStation = await SelectStationAsync(facade, "Введите название станции отправления:");
                //StationVO toStation = await SelectStationAsync(facade, "Введите название станции прибытия:");
                StationVO fromStation = new("ст. Речица, г. Речица, Гомельская обл., Беларусь", "Речица", "2100195");
                StationVO toStation = new("г. Минск, Беларусь", "Минск", "2100000");
                RouteVO route = new(fromStation, toStation);
                List<TrainVO> availableRoutes = await facade.GetTimesForRouteAsync(route);

                PrintRoutes(availableRoutes);

                Console.WriteLine("1 - Избранное\n2 - Подписки");
                int mainChoice = ParseUserChoice();

                if (mainChoice == 1)
                {
                    await ManageFavoritesAsync(facade, user1, availableRoutes);
                }
                else if (mainChoice == 2)
                {
                    await ManageSubscriptionsAsync(facade, user1, availableRoutes);
                }

                await PrintNotificationsAsync(facade);
                Console.WriteLine("----------------------------");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Ошибка: {ex.Message}");
            }
        }
    }

    private static async Task CheckNotificationsLoopAsync(Facade facade)
    {
        while (true)
        {
            Console.WriteLine("Введите 'n' для проверки уведомлений или любую клавишу для продолжения:");
            if (Console.ReadLine()?.ToLower() == "n")
            {
                await PrintNotificationsAsync(facade);
            }
            else
            {
                break;
            }
        }
    }

    private static async Task<StationVO> SelectStationAsync(Facade facade, string prompt)
    {
        Console.WriteLine(prompt);
        List<StationVO> stations = await facade.GetStationAsync(Console.ReadLine() ?? "");
        for (int i = 0; i < stations.Count; i++)
        {
            Console.WriteLine($"{i}: {stations[i].Label}");
        }
        Console.Write("Выберите номер станции: ");
        int index = ParseUserChoice();
        return stations[Math.Clamp(index, 0, stations.Count - 1)];
    }

    private static void PrintRoutes(List<TrainVO> routes)
    {
        Console.WriteLine("Маршруты:----------------------------");
        for (int i = 0; i < routes.Count; i++)
        {
            Console.WriteLine($"{i}: {routes[i].FromTime} --- {routes[i].ToTime}");
        }
    }

    private static int ParseUserChoice()
    {
        return int.TryParse(Console.ReadLine(), out int result) ? result : 0;
    }

    private static async Task ManageFavoritesAsync(Facade facade, string userId, List<TrainVO> routes)
    {
        await PrintFavoritesAsync(facade, userId);

        Console.WriteLine("1 - Добавить в избранное\n2 - Удалить из избранного");
        int action = ParseUserChoice();

        if (action == 1)
        {
            Console.Write("Введите номер маршрута для добавления: ");
            int index = ParseUserChoice();
            await facade.AddToFavoritesAsync(userId, routes[Math.Clamp(index, 0, routes.Count - 1)]);
        }
        else if (action == 2)
        {
            Console.Write("Введите номер маршрута для удаления: ");
            int index = ParseUserChoice();
            await facade.RemoveFromFavoritesAsync(userId, routes[Math.Clamp(index, 0, routes.Count - 1)]);
        }

        await PrintFavoritesAsync(facade, userId);
    }

    private static async Task ManageSubscriptionsAsync(Facade facade, string userId, List<TrainVO> routes)
    {
        await PrintSubscriptionsAsync(facade, userId);

        Console.WriteLine("1 - Подписаться\n2 - Отписаться");
        int action = ParseUserChoice();

        Console.Write("Введите дату (например, 30.04.2025): ");
        string dateInput = Console.ReadLine() ?? "01.01.2000";
        DateOnly date = DateOnly.Parse(dateInput);

        Console.Write("Введите номер маршрута: ");
        int routeIndex = ParseUserChoice();
        var selectedRoute = routes[Math.Clamp(routeIndex, 0, routes.Count - 1)];
        SubscriptionVO subscription = new(selectedRoute, date);

        if (action == 1)
        {
            await facade.SubscribeAsync(userId, subscription);
        }
        else if (action == 2)
        {
            await facade.UnSubscribeAsync(userId, subscription);
        }

        await PrintSubscriptionsAsync(facade, userId);
    }

    private static async Task PrintNotificationsAsync(Facade facade)
    {
        var notifications = await facade.PopNotifications();
        Console.WriteLine("Уведомления:----------------------------");
        foreach (var notification in notifications)
        {
            Console.WriteLine($"{notification.UserId}: {notification.Message}");
        }
    }

    private static async Task PrintFavoritesAsync(Facade facade, string userId)
    {
        var favorites = await facade.GetFavoritesAsync(userId);
        Console.WriteLine("Избранное:----------------------------");
        foreach (var item in favorites)
        {
            Console.WriteLine($"{item.FromTime} --- {item.ToTime}");
        }
    }

    private static async Task PrintSubscriptionsAsync(Facade facade, string userId)
    {
        var subscriptions = await facade.GetSubscritionsAsync(userId);
        Console.WriteLine("Подписки:----------------------------");
        foreach (var subscription in subscriptions)
        {
            Console.WriteLine($"Дата: {subscription.Date}");
            Console.WriteLine($"{subscription.Train.FromTime} --- {subscription.Train.ToTime}\n");
        }
    }
}
