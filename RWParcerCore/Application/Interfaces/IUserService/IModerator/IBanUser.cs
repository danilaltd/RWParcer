namespace RWParcerCore.Application.Interfaces.IUserService.IModerator
{
    internal interface IBanUser
    {
        Task BanUserAsync(string userId, string targetId);
    }
}
