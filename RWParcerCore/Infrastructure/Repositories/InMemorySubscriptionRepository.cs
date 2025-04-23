using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;
using System.Diagnostics;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemorySubscriptionRepository : ISubscriptionRepository
    {
        private readonly List<SubscriptionItem> _subscriptions = [];
        private readonly SemaphoreSlim _semaphore = new(1, 1); // Потокобезопасный механизм блокировки

        public async Task<IEnumerable<SubscriptionItem>> GetSubscriptionsAsync(string userId)
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

        public async Task AddSubscriptionAsync(SubscriptionItem subscriptionItem)
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

        public async Task<bool> ExistsAsync(string userId, SubscriptionVO subscription)
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
                    f.Subscription.Equals(subscription));
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task RemoveSubscriptionAsync(SubscriptionItem subscriptionItem)
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

        public async Task<IEnumerable<SubscriptionItem>> GetAllSubscriptionsAsync()
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
    }



}
