using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface ISubscriptionRepository
    {
        Task<IEnumerable<Subscription>> GetUserSubscriptionsAsync(string userId);
        Task<IEnumerable<Subscription>> GetAllSubscriptionsAsync();
        Task AddSubscriptionAsync(Subscription subscriptionItem);
        Task RemoveSubscriptionAsync(Subscription subscription);
        Task<bool> SubscriptionExistsAsync(string userId, SubscriptionVO subscription);
    }
}
