//StationVO fromStation = new("ст. Речица, г. Речица, Гомельская обл., Беларусь", "Речица", "2100195");
//StationVO toStation = new("г. Минск, Беларусь", "Минск", "2100000");

using RWParcerCore.InterfaceAdapters.Facades;
using RWParcerCore.Domain.ValueObjects;

class Program
{
    static async Task Main()
    {
        Facade facade = new();
        string userId = "12345";
        facade.AuthenticateUser(userId);

        Console.WriteLine("RWParcer Tester started!");

        while (true)
        {
            try
            {
                Console.WriteLine(@"
1. Get stations
2. Get trains between stations
3. Favorites
4. Subscriptions
5. Pop notifications
6. Manage Users
0. Exit
Choose an option:");

                switch (Console.ReadLine())
                {
                    case "1":
                        await GetStationsAsync(facade);
                        break;

                    case "2":
                        await GetTrainsAsync(facade);
                        break;

                    case "3":
                        await ManageFavoritesAsync(facade, userId);
                        break;

                    case "4":
                        await ManageSubscriptionsAsync(facade, userId);
                        break;

                    case "5":
                        await PrintNotificationsAsync(facade);
                        break;

                    case "6":
                        await ManageUsersAsync(facade);
                        break;

                    case "0":
                        await facade.StopAsync();
                        return;

                    default:
                        Console.WriteLine("Invalid choice!");
                        break;
                }

                Console.WriteLine("Press Enter to continue...");
                Console.ReadLine();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Ошибка: {ex.Message}");
            }
        }
    }

    static async Task GetStationsAsync(Facade facade)
    {
        Console.Write("Enter station prefix: ");
        var stations = await facade.GetStationAsync(Console.ReadLine() ?? "");

        for (int i = 0; i < stations.Count; i++)
        {
            Console.WriteLine($"{i}: {stations[i].Label}");
        }
    }

    static async Task GetTrainsAsync(Facade facade)
    {
        Console.Write("From station prefix: ");
        var fromList = await facade.GetStationAsync(Console.ReadLine() ?? "");
        PrintStations(fromList);
        var from = fromList[ReadIndex(fromList.Count)];

        Console.Write("To station prefix: ");
        var toList = await facade.GetStationAsync(Console.ReadLine() ?? "");
        PrintStations(toList);
        var to = toList[ReadIndex(toList.Count)];

        var trains = await facade.GetTimesForRouteAsync(new RouteVO(from, to));
        PrintTrains(trains);
    }

    static async Task ManageFavoritesAsync(Facade facade, string userId)
    {
        var favorites = await facade.GetFavoritesAsync(userId);
        Console.WriteLine("Favorites:");
        PrintTrains(favorites);

        Console.WriteLine("1. Add\n2. Remove");
        var choice = Console.ReadLine();
        if (choice is "1" or "2")
        {
            await GetTrainsAsync(facade);
            Console.Write("Choose train index: ");
            StationVO fromStation = new("ст. Речица, г. Речица, Гомельская обл., Беларусь", "Речица", "2100195");
            StationVO toStation = new("г. Минск, Беларусь", "Минск", "2100000");
            var route = await facade.GetTimesForRouteAsync(new(fromStation, toStation)); // Example route
            var train = route[ReadIndex(route.Count)];

            if (choice == "1")
                await facade.AddToFavoritesAsync(userId, train);
            else
                await facade.RemoveFromFavoritesAsync(userId, train);
        }
    }

    static async Task ManageSubscriptionsAsync(Facade facade, string userId)
    {
        var subs = await facade.GetSubscritionsAsync(userId);
        Console.WriteLine("Subscriptions:");
        foreach (var sub in subs)
        {
            Console.WriteLine($"{sub.Date}: {sub.Train.FromTime} - {sub.Train.ToTime}");
        }

        Console.WriteLine("1. Subscribe\n2. Unsubscribe");
        var choice = Console.ReadLine();
        if (choice is "1" or "2")
        {
            await GetTrainsAsync(facade);
            Console.Write("Choose train index: ");
            StationVO fromStation = new("ст. Речица, г. Речица, Гомельская обл., Беларусь", "Речица", "2100195");
            StationVO toStation = new("г. Минск, Беларусь", "Минск", "2100000");
            var route = await facade.GetTimesForRouteAsync(new(fromStation, toStation)); // Example route
            var train = route[ReadIndex(route.Count)];

            Console.Write("Enter date (yyyy-MM-dd): ");
            var date = DateOnly.Parse(Console.ReadLine() ?? "2000-01-01");

            var subscription = new SubscriptionVO(train, date);

            if (choice == "1")
                await facade.SubscribeAsync(userId, subscription);
            else
                await facade.UnSubscribeAsync(userId, subscription);
        }
    }

    static async Task PrintNotificationsAsync(Facade facade)
    {
        var notifications = await facade.PopNotifications();
        foreach (var notif in notifications)
        {
            Console.WriteLine($"{notif.UserId}: {notif.Message}");
        }
    }

    static void PrintStations(List<StationVO> stations)
    {
        for (int i = 0; i < stations.Count; i++)
        {
            Console.WriteLine($"{i}: {stations[i].Label}");
        }
    }

    static void PrintTrains(List<TrainVO> trains)
    {
        for (int i = 0; i < trains.Count; i++)
        {
            Console.WriteLine($"{i}: {trains[i].FromTime} -> {trains[i].ToTime}");
        }
    }

    static int ReadIndex(int max)
    {
        while (true)
        {
            if (int.TryParse(Console.ReadLine(), out int index) && index >= 0 && index < max)
                return index;
            Console.Write("Invalid index, try again: ");
        }
    }

    static async Task ManageUsersAsync(Facade facade)
    {
        Console.WriteLine(@"
User Management:
1. Authenticate new user
2. Get user status
3. Ban user
4. Unban user
5. Set max subscriptions
6. Set min interval
7. Promote
8. Demote
Choose option:");

        string? choice = Console.ReadLine();

        Console.Write("Enter current user ID: ");
        string curUserId = Console.ReadLine() ?? "user";
        string targetUserId;
        switch (choice)
        {
            case "1":
                facade.AuthenticateUser(curUserId);
                Console.WriteLine("User authenticated.");
                break;

            case "2":
                string status = await facade.GetUserStatusAsync(curUserId);
                Console.WriteLine($"Status of {curUserId}: {status}");
                break;

            case "3":
                Console.Write("Enter target user ID: ");
                targetUserId = Console.ReadLine() ?? "user";
                await facade.BanUserAsync(curUserId, targetUserId);
                Console.WriteLine("User banned.");
                break;

            case "4":
                Console.Write("Enter target user ID: ");
                targetUserId = Console.ReadLine() ?? "user";
                await facade.UnbanUserAsync(curUserId, targetUserId);
                Console.WriteLine("User unbanned.");
                break;

            case "5":
                Console.Write("Enter max subscriptions (uint): ");
                if (uint.TryParse(Console.ReadLine(), out uint maxSub))
                {
                    Console.Write("Enter target user ID: ");
                    targetUserId = Console.ReadLine() ?? "user";
                    await facade.SetUsersMaxSubscriptionsAsync(curUserId, targetUserId, maxSub);
                    Console.WriteLine("Max subscriptions updated.");
                }
                else
                {
                    Console.WriteLine("Invalid input.");
                }
                break;

            case "6":
                Console.Write("Enter min interval (uint): ");
                if (uint.TryParse(Console.ReadLine(), out uint minInt))
                {
                    Console.Write("Enter target user ID: ");
                    targetUserId = Console.ReadLine() ?? "user";
                    await facade.SetUsersMinIntervalAsync(curUserId, targetUserId, minInt);
                    Console.WriteLine("Min interval updated.");
                }
                else
                {
                    Console.WriteLine("Invalid input.");
                }
                break;

            case "7":
                Console.Write("Enter target user ID: ");
                targetUserId = Console.ReadLine() ?? "user";
                await facade.PromoteUserAsync(curUserId, targetUserId);
                Console.WriteLine("User promoted.");
                break;

            case "8":
                Console.Write("Enter target user ID: ");
                targetUserId = Console.ReadLine() ?? "user";
                await facade.DemoteUserAsync(curUserId, targetUserId);
                Console.WriteLine("User demoted.");
                break;

            default:
                Console.WriteLine("Unknown command.");
                break;
        }
    }

}
