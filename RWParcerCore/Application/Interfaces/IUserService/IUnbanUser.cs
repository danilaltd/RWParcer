namespace RWParcerCore.Application.Interfaces.IUserService
{
    internal interface IUnbanUser
    {
        Task UnbanUserAsync(string userId, string targetId);
    }
}
