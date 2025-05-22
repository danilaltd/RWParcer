using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface ISubscriptionRepository
    {
        Task<IEnumerable<Subscription>> GetUserSubscriptionsAsync(string userId);
        Task<IEnumerable<Subscription>> GetAllSubscriptionsAsync();
        Task AddAsync(Subscription subscriptionItem);
        Task RemoveAsync(Subscription subscription);
        Task<bool> SubscriptionExistsAsync(string userId, SubscriptionVO subscription);
        Task<uint> GetSubscriptionCountAsync(string userId);
        Task UpdateAsync(Subscription subscription);
        Task ResetAsync(Subscription subscription);
    }
}
