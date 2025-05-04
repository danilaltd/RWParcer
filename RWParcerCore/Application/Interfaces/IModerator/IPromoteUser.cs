namespace RWParcerCore.Application.Interfaces.IModerator
{
    internal interface IPromoteUser
    {
        Task PromoteUserAsync(string userId, string targetId);
    }
}
