using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.Interfaces;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Infrastructure.InMemoryRepositories
{
    internal class InMemorySubscriptionRepository(ILogger logger) : ISubscriptionRepository
    {
        private readonly List<Subscription> _subscriptions = [];
        private readonly SemaphoreSlim _semaphore = new(1, 1); // Потокобезопасный механизм блокировки
        private readonly ILogger _logger = logger;

        public async Task<IEnumerable<Subscription>> GetUserSubscriptionsAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                return [.. _subscriptions.Where(f => f.UserId == userId)];
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task AddAsync(Subscription subscriptionItem)
        {
            if (subscriptionItem == null)
            {
                _logger.LogDebug("AddSubscription err");
                return;
            }

            await _semaphore.WaitAsync();
            try
            {
                _subscriptions.Add(subscriptionItem);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<bool> SubscriptionExistsAsync(string userId, SubscriptionVO subscription)
        {
            if (subscription is null)
            {
                _logger.LogDebug("Exists err");
                return false;
            }

            await _semaphore.WaitAsync();
            try
            {
                return _subscriptions.Any(f =>
                    f.UserId.ToString() == userId &&
                    f.Details.Equals(subscription));
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task RemoveAsync(Subscription subscriptionItem)
        {
            if (subscriptionItem == null)
            {
                _logger.LogDebug("RemoveSubscription err");
                return;
            }

            await _semaphore.WaitAsync();
            try
            {
                _subscriptions.Remove(subscriptionItem);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<IEnumerable<Subscription>> GetAllSubscriptionsAsync()
        {
            await _semaphore.WaitAsync();
            try
            {
                return [.. _subscriptions];
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<uint> GetSubscriptionCountAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                return (uint)_subscriptions.Count(s => s.UserId == userId);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task UpdateAsync(Subscription subscription)
        {
            await _semaphore.WaitAsync();
            try
            {
                var index = _subscriptions.FindIndex(s => s.Id == subscription.Id);
                if (index == -1)
                    throw new KeyNotFoundException($"Subscription with ID {subscription.Id} not found");

                _subscriptions[index] = subscription; // Полностью заменяем объект подписки
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task ResetAsync(Subscription subscriptionItem)
        {
            if (subscriptionItem == null)
            {
                _logger.LogDebug("RemoveSubscription err");
                return;
            }

            await _semaphore.WaitAsync();
            try
            {
                subscriptionItem.LastState = [];
                subscriptionItem.LastUpdate = null;
            }
            finally
            {
                _semaphore.Release();
            }
        }
    }



}
