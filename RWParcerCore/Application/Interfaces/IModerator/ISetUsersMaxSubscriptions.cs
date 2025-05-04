namespace RWParcerCore.Application.Interfaces.IModerator
{
    internal interface ISetUsersMaxSubscriptions
    {
        Task SetUsersMaxSubscriptionsAsync(string userId, string targetId, uint maxSubscriptions);
    }
}
