namespace RWParcerCore.Application.Interfaces.IUserService
{
    internal interface IDemoteUser
    {
        Task DemoteUserAsync(string userId, string targetId);
    }
}
