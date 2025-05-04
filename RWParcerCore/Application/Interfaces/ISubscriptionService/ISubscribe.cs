using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.ISubscriptionService
{
    internal interface ISubscribe
    {
        Task SubscribeAsync(string userId, SubscriptionVO subscription);
    }
}
