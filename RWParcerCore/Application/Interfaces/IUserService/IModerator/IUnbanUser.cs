namespace RWParcerCore.Application.Interfaces.IUserService.IModerator
{
    internal interface IUnbanUser
    {
        Task UnbanUserAsync(string userId, string targetId);
    }
}
