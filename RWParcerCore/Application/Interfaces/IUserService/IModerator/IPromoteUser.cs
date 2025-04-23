namespace RWParcerCore.Application.Interfaces.IUserService.IModerator
{
    internal interface IPromoteUser
    {
        Task PromoteUserAsync(string userId, string targetId);
    }
}
