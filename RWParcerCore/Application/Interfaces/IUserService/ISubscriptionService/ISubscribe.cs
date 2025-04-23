using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService
{
    internal interface ISubscribe
    {
        Task SubscribeAsync(string userId, SubscriptionVO subscription);
    }
}
