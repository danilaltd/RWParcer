using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.IServices;
using RWParcerCore.Domain.ValueObjects;
using System.Diagnostics;
using static System.Runtime.InteropServices.JavaScript.JSType;

namespace RWParcerCore.Infrastructure.Services
{
    internal class NotificationBackgroundService(ISubscriptionRepository subscriptionRepository, INotificationRepository notificationRepository, IUserRepository userRepository, IRWRepository rwRepository, int maxRetries, int threadingMax) : INotificationBackgroundService
    {
        private readonly ISubscriptionRepository _subscriptionRepository = subscriptionRepository;
        private readonly INotificationRepository _notificationRepository = notificationRepository;
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IRWRepository _rwRepository = rwRepository;
        private readonly SemaphoreSlim _semaphore = new(threadingMax);
        private readonly int _maxRetries = maxRetries;

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            Console.Write("Waiting...");
            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    var subscriptions = await _subscriptionRepository.GetAllSubscriptionsAsync();
                    if (!subscriptions.Any())
                    {
                        await Task.Delay(10, cancellationToken);
                    }

                    if (await UnsubscribeExpiredAsync(subscriptions)) continue;

                    var tasks = subscriptions.Select(subscription => ProcessSubscriptionAsync(subscription, cancellationToken)).ToArray();
                    await Task.WhenAll(tasks);
                } catch (Exception ex)
                {
                    Console.WriteLine($"Неизвестная ошибка: {ex.Message}");
                }
            }
        }

        private async Task<bool> UnsubscribeExpiredAsync(IEnumerable<Subscription> subscriptions)
        {
            DateOnly curDate = DateOnly.FromDateTime(DateTime.UtcNow);
            var expiredSubscriptions = subscriptions.Where(s => s.Details.Date < curDate).ToList();

            if (expiredSubscriptions.Any())
            {
                foreach (var subscription in expiredSubscriptions)
                {
                    await _subscriptionRepository.RemoveAsync(subscription);
                }
                return true;
            }
            return false;
        }

        private async Task ProcessSubscriptionAsync(Subscription subscription, CancellationToken cancellationToken)
        {
            await _semaphore.WaitAsync(cancellationToken);
            try
            {
                for (int attempt = 1; attempt <= _maxRetries; attempt++)
                {
                    try
                    {
                        if (DateTime.UtcNow - subscription.LastUpdate < TimeSpan.FromSeconds(await _userRepository.GetUserMinIntervalAsync(subscription.UserId))) break;
                        Console.WriteLine($"Попытка {attempt}: Запрос {subscription.Id}");
                        var response = await _rwRepository.GetSeatsAsync(subscription.Details);
                        if (!AreStatesEqual(response, subscription.LastState))
                        {
                            Console.WriteLine($"Изменение данных для {subscription.Id}\n");
                            var changes = FindSeatChanges(subscription.LastState, response);
                            if (changes.Count > 0)
                            {
                                string changeMessage = $"{subscription.Details.Date:dd.MM.yyyy}\n{Convert(subscription.Details.Train)}\n{(subscription.LastState is not null ? "Изменены места" : "Свободные места")}: \n{string.Join("\n", changes)}";
                                await _notificationRepository.AddAsync(new(Guid.NewGuid(), subscription.UserId, changeMessage));
                            }
                            else if (response.Count != 0)
                            {
                                throw new Exception($"unsupported changes {subscription.Id}");
                            }
                            subscription.LastState = response;

                        }
                        subscription.LastUpdate = DateTime.UtcNow;
                        await _subscriptionRepository.UpdateAsync(subscription);
                        break;
                    }
                    catch (TaskCanceledException)
                    {
                        Console.WriteLine($"Тайм-аут запроса для {subscription.Id} (Попытка {attempt})");
                    }
                    catch (HttpRequestException ex)
                    {
                        Console.WriteLine($"Ошибка HTTP ({subscription.Id}, Попытка {attempt}): {ex.Message}");
                    }
                    catch (Exception ex)
                    {
                        Console.WriteLine($"Неизвестная ошибка ({subscription.Id}, Попытка {attempt}): {ex.Message}");
                    }
                }
            }
            finally
            {
                _semaphore.Release();
            }
        }

        private static bool AreStatesEqual(List<CarVO> l1, List<CarVO> l2)
        {
            return l1 is not null && l2 is not null &&
                   l1.Count == l2.Count &&
                   l1.OrderBy(x => x.Number).Zip(l2.OrderBy(x => x.Number)).All(pair => pair.First == pair.Second);
        }

        private static List<string> FindSeatChanges(List<CarVO>? oldState, List<CarVO>? newState)
        {
            var changes = new List<string>();

            var oldStateSafe = oldState ?? [];
            var newStateSafe = newState ?? [];

            foreach (var oldCar in oldStateSafe.OrderBy(c => c.Number))
            {
                var newCar = newStateSafe.FirstOrDefault(c => c.Number == oldCar.Number);

                if (newCar is not null)
                {
                    var removedSeats = (oldCar.FreeSeats ?? []).Except(newCar.FreeSeats ?? []).ToList();
                    var addedSeats = (newCar.FreeSeats ?? []).Except(oldCar.FreeSeats ?? []).ToList();

                    if (removedSeats.Count > 0)
                        changes.Add($"{Convert(oldCar.Type)} №{oldCar.Number}: Удалены места {string.Join(", ", removedSeats)}");

                    if (addedSeats.Count > 0)
                        changes.Add($"{Convert(oldCar.Type)} №{oldCar.Number}: Добавлены места {string.Join(", ", addedSeats)}");
                }
                else
                {
                    changes.Add($"{Convert(oldCar.Type)} №{oldCar.Number}: Все места удалены");
                }
            }

            foreach (var newCar in newStateSafe.OrderBy(c => c.Number))
            {
                if (!oldStateSafe.Any(c => c.Number == newCar.Number))
                {
                    changes.Add($"{Convert(newCar.Type)} №{newCar.Number}: Новый вагон, места {string.Join(", ", newCar.FreeSeats ?? [])}");
                }
            }

            return changes;
        }


        private static string Convert(TrainVO train)
        {
            string route = train.StationFrom.Label + " - " + train.StationTo.Label;
            string times = $"{train.FromTime:HH:mm}→{train.ToTime:HH:mm}";

            return string.Join("\n", route, times);
        }

        private static string Convert(CarType type)
        {
            return type switch
            {
                CarType.Common => "Общий вагон",
                CarType.Seat => "Сидячий вагон",
                CarType.Platzkart => "Плацкартный вагон",
                CarType.Coupe => "Купейный вагон",
                CarType.Soft => "Мягкий вагон",
                CarType.SV => "Вагон СВ",
                _ => "Вагон неизвестного типа"
            };
        }

    }



}
