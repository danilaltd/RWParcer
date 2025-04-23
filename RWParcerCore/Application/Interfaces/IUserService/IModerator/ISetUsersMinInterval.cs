namespace RWParcerCore.Application.Interfaces.IUserService.IModerator
{
    internal interface ISetUsersMinInterval
    {
        Task SetUsersMinIntervalAsync(string userId, string targetId, uint minInterval);
    }
}
