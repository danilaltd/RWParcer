using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.IServices;
using System.Diagnostics;

namespace RWParcerCore.Infrastructure.Services
{
    internal class NotificationBackgroundService(ISubscriptionRepository subscriptionRepository, INotificationRepository notificationRepository, IRWRepository rwRepository, int maxRetries, int threadingMax) : INotificationBackgroundService
    {
        private readonly ISubscriptionRepository _subscriptionRepository = subscriptionRepository;
        private readonly INotificationRepository _notificationRepository = notificationRepository;
        private readonly IRWRepository _rwRepository = rwRepository;
        private readonly SemaphoreSlim _semaphore = new(threadingMax);
        private readonly int _maxRetries = maxRetries;

        public async Task StartAsync(CancellationToken cancellationToken)
        {
            Debug.Write("Waiting...");
            while (!cancellationToken.IsCancellationRequested)
            {
                var subscriptions = await _subscriptionRepository.GetAllSubscriptionsAsync();
                if (!subscriptions.Any())
                {
                    await Task.Delay(10);
                }

                var tasks = subscriptions.Select(subscription => ProcessSubscriptionAsync(subscription, cancellationToken)).ToArray();
                await Task.WhenAll(tasks);
            }
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
                        if (DateTime.Now - subscription.LastUpdate < TimeSpan.FromSeconds(subscription.Interval)) break;
                        Debug.WriteLine($"Попытка {attempt}: Запрос {subscription.Id}");
                        var response = await _rwRepository.GetSeatsAsync(subscription.Details);
                        if (!AreDictionariesEqual(response, subscription.LastState))
                        {
                            Debug.WriteLine($"Изменение данных для {subscription.Id}\n");
                            var changes = FindSeatChanges(subscription.LastState, response);
                            if (changes.Count > 0)
                            {
                                string changeMessage = $"{(subscription.LastState is not null ? "Изменены места" : "Свободные места")}: \n{string.Join("\n", changes)}";
                                await _notificationRepository.AddAsync(new(Guid.NewGuid(), subscription.UserId, changeMessage));
                            }
                            else if (response.Count != 0)
                            {
                                throw new Exception($"unsupported changes {subscription.Id}");
                            }
                            subscription.LastState = response;

                        }
                        subscription.LastUpdate = DateTime.Now;

                        break;
                    }
                    catch (TaskCanceledException)
                    {
                        Debug.WriteLine($"Тайм-аут запроса для {subscription.Id} (Попытка {attempt})");
                    }
                    catch (HttpRequestException ex)
                    {
                        Debug.WriteLine($"Ошибка HTTP ({subscription.Id}, Попытка {attempt}): {ex.Message}");
                    }
                    catch (Exception ex)
                    {
                        Debug.WriteLine($"Неизвестная ошибка ({subscription.Id}, Попытка {attempt}): {ex.Message}");
                    }
                }
            }
            finally
            {
                _semaphore.Release();
            }
        }

        private static bool AreDictionariesEqual(Dictionary<int, List<int>>? dict1, Dictionary<int, List<int>>? dict2)
        {
            return dict1 != null && dict2 != null && 
                   dict1.Count == dict2.Count &&
                   dict1.Keys.All(dict2.ContainsKey) &&
                   dict1.All(pair => dict2[pair.Key].OrderBy(x => x).SequenceEqual(pair.Value.OrderBy(x => x)));
        }

        private static List<string> FindSeatChanges(Dictionary<int, List<int>>? oldState, Dictionary<int, List<int>>? newState)
        {
            var changes = new List<string>();

            var oldStateSafe = oldState ?? [];
            var newStateSafe = newState ?? [];

            foreach (var carNumber in oldStateSafe.Keys.OrderBy(x => x))
            {
                if (newStateSafe.TryGetValue(carNumber, out var newSeats))
                {
                    var removedSeats = oldStateSafe[carNumber].Except(newSeats).ToList();
                    var addedSeats = newSeats.Except(oldStateSafe[carNumber]).ToList();

                    if (removedSeats.Count != 0)
                        changes.Add($"Вагон {carNumber}: Удалены {string.Join(", ", removedSeats)}");

                    if (addedSeats.Count != 0)
                        changes.Add($"Вагон {carNumber}: Добавлены {string.Join(", ", addedSeats)}");
                }
                else
                {
                    changes.Add($"Вагон {carNumber}: Все места удалены");
                }
            }

            foreach (var carNumber in newStateSafe.Keys.OrderBy(x => x))
            {
                if (!oldStateSafe.ContainsKey(carNumber))
                {
                    changes.Add($"Вагон {carNumber}: Новый вагон, места {string.Join(", ", newStateSafe[carNumber])}");
                }
            }

            return changes;
        }


    }

}
