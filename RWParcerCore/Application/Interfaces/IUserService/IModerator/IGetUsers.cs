using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IUserService.IModerator
{
    internal interface IGetUsers
    {
        Task<List<UserVO>> GetUsersAsync(string userId, TimeSpan timeSpan);
    }
}
