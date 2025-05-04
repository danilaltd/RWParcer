namespace RWParcerCore.Application.Interfaces.IUserService
{
    internal interface IIsUserBanned
    {
        Task<bool> IsUserBannedAsync(string userId, string targetId);
    }
}
