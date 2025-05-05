using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;
using System.Diagnostics;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemorySubscriptionRepository : ISubscriptionRepository
    {
        private readonly List<Subscription> _subscriptions = [];
        private readonly SemaphoreSlim _semaphore = new(1, 1); // Потокобезопасный механизм блокировки

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
                Debug.WriteLine("AddSubscription err");
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
                Debug.WriteLine("Exists err");
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
                Debug.WriteLine("RemoveSubscription err");
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
    }



}
