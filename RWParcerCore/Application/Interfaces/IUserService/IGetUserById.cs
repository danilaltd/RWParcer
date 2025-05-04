using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IUserService
{
    internal interface IGetUserById
    {
        Task<UserVO> GetUserByIdAsync(string userId, string targetId);
    }
}
