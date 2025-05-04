namespace RWParcerCore.Application.Interfaces.IModerator
{
    internal interface IDemoteUser
    {
        Task DemoteUserAsync(string userId, string targetId);
    }
}
