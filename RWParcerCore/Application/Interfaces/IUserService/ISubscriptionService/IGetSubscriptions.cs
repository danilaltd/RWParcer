using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService
{
    internal interface IGetSubscriptions
    {
        Task<List<SubscriptionVO>> GetSubscriptionsAsync(string userId);
    }
}
