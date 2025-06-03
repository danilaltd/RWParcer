using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.Interfaces;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.IServices;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Infrastructure.Services
{
    internal class NotificationBackgroundService(ISubscriptionRepository subscriptionRepository, INotificationRepository notificationRepository, IUserRepository userRepository, IRWRepository rwRepository, ILogger logger, int maxRetries, int threadingMax) : INotificationBackgroundService
    {
        private readonly ISubscriptionRepository _subscriptionRepository = subscriptionRepository;
        private readonly INotificationRepository _notificationRepository = notificationRepository;
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IRWRepository _rwRepository = rwRepository;
        private readonly SemaphoreSlim _semaphore = new(threadingMax);
        private readonly int _maxRetries = maxRetries;
        private readonly ILogger _logger = logger;


        public async Task StartAsync(CancellationToken cancellationToken)
        {
            _logger.LogDebug("Waiting...");
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
                }
                catch (Exception ex)
                {
                    _logger.LogDebug($"Неизвестная ошибка: {ex.Message}");
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
                        _logger.LogDebug($"Попытка {attempt}: Запрос {subscription.Id}");
                        var response = await _rwRepository.GetSeatsAsync(subscription.Details);
                        var actualSubscription = await _subscriptionRepository.GetByIdAsync(subscription.Id);
                        if (actualSubscription == null) break;
                        if (!AreStatesEqual(response, actualSubscription.LastState))
                        {
                            _logger.LogDebug($"Изменение данных для {subscription.Id}\n");
                            var changes = FindSeatChanges(actualSubscription.LastState, response);
                            if (changes.Count > 0)
                            {
                                string changeMessage = $"{subscription.Details.Date:dd.MM.yyyy}\n{Convert(subscription.Details.Train)}\n{(actualSubscription.LastState is not null ? "Изменены места" : "Свободные места")}: \n{string.Join("\n", changes)}";
                                await _notificationRepository.AddAsync(new(Guid.NewGuid(), subscription.UserId, changeMessage));
                            }
                            else if (response.Count != 0)
                            {
                                throw new Exception($"unsupported changes {subscription.Id}");
                            }
                            actualSubscription.LastState = response;
                            await _subscriptionRepository.UpdateAsync(actualSubscription);
                        }
                        actualSubscription.LastUpdate = DateTime.UtcNow;
                        await _subscriptionRepository.UpdateAsync(actualSubscription);
                        break;
                    }
                    catch (TaskCanceledException)
                    {
                        _logger.LogDebug($"Тайм-аут запроса для {subscription.Id} (Попытка {attempt})");
                    }
                    catch (HttpRequestException ex)
                    {
                        _logger.LogDebug($"Ошибка HTTP ({subscription.Id}, Попытка {attempt}): {ex.Message}");
                    }
                    catch (Exception ex)
                    {
                        _logger.LogDebug($"Неизвестная ошибка ({subscription.Id}, Попытка {attempt}): {ex.Message}");
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
                        changes.Add($"{Convert(oldCar.Type)} №{oldCar.Number}: Заняты места {string.Join(", ", removedSeats)}");

                    if (addedSeats.Count > 0)
                        changes.Add($"{Convert(oldCar.Type)} №{oldCar.Number}: Освобождены места {string.Join(", ", addedSeats)}");
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
