using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.ISubscriptionService
{
    internal interface IResetSubscribe
    {
        Task ResetSubscribeAsync(string userId, SubscriptionVO subscription);
    }
}
