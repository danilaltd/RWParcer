using RWParcerCore.Domain.Entities;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface IUserRepository
    {
        Task<bool> IsUserRegistredAsync(string userId);
        Task AddAsync(User newUser);
        Task<uint> GetUserMinIntervalAsync(string userId);
        Task<bool> IsUserModeratorAsync(string userId);
        Task<uint> GetUserMaxSubscriptionsAsync(string userId);
        Task SetUsersMinIntervalAsync(string userId, uint minInterval);
        Task SetUsersMaxSubscriptionsAsync(string userId, uint MaxSubscriptions);
        Task BanUserAsync(string userId);
        Task UnbanUserAsync(string userId);
        Task PromoteUserAsync(string userId);
        Task DemoteUserAsync(string userId);
        Task<bool> IsUserBannedAsync(string userId);
        Task UpdateActivityAsync(string userId);
        Task<List<User>> GetLastUsersAsync(TimeSpan timeSpan);
        Task<User> GetUserByIdAsync(string userId);
        Task<List<User>> GetAllModerators();
    }
}
