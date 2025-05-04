namespace RWParcerCore.Application.Interfaces.IUserService
{
    internal interface IIsUserModerator
    {
        Task<bool> IsUserModeratorAsync(string userId, string targetId);
    }
}
