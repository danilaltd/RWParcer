using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface ISubscriptionRepository
    {
        Task<IEnumerable<SubscriptionItem>> GetSubscriptionsAsync(string userId);
        Task<IEnumerable<SubscriptionItem>> GetAllSubscriptionsAsync();
        Task AddSubscriptionAsync(SubscriptionItem subscriptionItem);
        Task RemoveSubscriptionAsync(SubscriptionItem subscription);
        Task<bool> ExistsAsync(string userId, SubscriptionVO subscription);
    }
}
