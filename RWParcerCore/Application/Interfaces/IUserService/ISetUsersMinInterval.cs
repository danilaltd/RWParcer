namespace RWParcerCore.Application.Interfaces.IUserService
{
    internal interface ISetUsersMinInterval
    {
        Task SetUsersMinIntervalAsync(string userId, string targetId, uint minInterval);
    }
}
