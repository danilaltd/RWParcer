using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService
{
    internal interface IUnSubscribe
    {
        Task UnSubscribeAsync(string userId, SubscriptionVO subscription);
    }
}
