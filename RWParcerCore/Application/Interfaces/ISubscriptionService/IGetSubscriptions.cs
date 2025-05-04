using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.ISubscriptionService
{
    internal interface IGetSubscriptions
    {
        Task<List<SubscriptionVO>> GetSubscriptionsAsync(string userId, string targetId);
    }
}
