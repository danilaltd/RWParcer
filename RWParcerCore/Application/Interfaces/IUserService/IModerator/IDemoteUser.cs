namespace RWParcerCore.Application.Interfaces.IUserService.IModerator
{
    internal interface IDemoteUser
    {
        Task DemoteUserAsync(string userId, string targetId);
    }
}
