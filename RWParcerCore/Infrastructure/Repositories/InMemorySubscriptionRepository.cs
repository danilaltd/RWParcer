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

        public async Task AddSubscriptionAsync(Subscription subscriptionItem)
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

        public async Task RemoveSubscriptionAsync(Subscription subscriptionItem)
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
    }



}
