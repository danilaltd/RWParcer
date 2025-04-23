namespace RWParcerCore.Application.Interfaces.IUserService.IModerator
{
    internal interface ISetUsersMaxSubscriptions
    {
        Task SetUsersMaxSubscriptionsAsync(string userId, string targetId, uint maxSubscriptions);
    }
}
