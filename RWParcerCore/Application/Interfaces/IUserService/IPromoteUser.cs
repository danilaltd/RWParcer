namespace RWParcerCore.Application.Interfaces.IUserService
{
    internal interface IPromoteUser
    {
        Task PromoteUserAsync(string userId, string targetId);
    }
}
