namespace RWParcerCore.Application.Interfaces.IModerator
{
    internal interface ISetUsersMinInterval
    {
        Task SetUsersMinIntervalAsync(string userId, string targetId, uint minInterval);
    }
}
