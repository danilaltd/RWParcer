namespace RWParcerCore.Application.Interfaces.IUserService
{
    internal interface ISetUsersMaxSubscriptions
    {
        Task SetUsersMaxSubscriptionsAsync(string userId, string targetId, uint maxSubscriptions);
    }
}
