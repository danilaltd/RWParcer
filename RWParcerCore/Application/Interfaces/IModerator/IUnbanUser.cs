namespace RWParcerCore.Application.Interfaces.IModerator
{
    internal interface IUnbanUser
    {
        Task UnbanUserAsync(string userId, string targetId);
    }
}
