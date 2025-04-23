using RWParcerCore.Domain.Entities;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface IUserRepository
    {
        Task<User?> GetUserByIdAsync(string id);
        Task AddUserAsync(User newUser);
        Task<uint> GetUserMinIntervalAsync(string id);
    }
}
