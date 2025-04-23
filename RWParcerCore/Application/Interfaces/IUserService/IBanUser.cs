namespace RWParcerCore.Application.Interfaces.IUserService
{
    internal interface IBanUser
    {
        Task BanUserAsync(string userId, string targetId);
    }
}
