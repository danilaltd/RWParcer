namespace RWParcerCore.Application.Interfaces.IModerator
{
    internal interface IBanUser
    {
        Task BanUserAsync(string userId, string targetId);
    }
}
