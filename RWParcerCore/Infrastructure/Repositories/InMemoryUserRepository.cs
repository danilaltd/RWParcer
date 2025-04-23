using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemoryUserRepository : IUserRepository
    {
        private readonly List<User> _users = [];
        private readonly SemaphoreSlim _semaphore = new(1, 1); // Потокобезопасный механизм блокировки

        public async Task<bool> IsUserRegistredAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                return _users.FirstOrDefault(u => u.Id == userId) != null;
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task AddUserAsync(User user)
        {
            await _semaphore.WaitAsync();
            try
            {
                _users.Add(user);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<uint> GetUserMinIntervalAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                var user = _users.FirstOrDefault(u => u.Id == userId);
                return user is null ? throw new KeyNotFoundException($"User with ID {userId} not found") : user.MinSubscriptionsInterval;
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<bool> IsUserModeratorAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                var user = _users.FirstOrDefault(u => u.Id == userId);
                return user is null ? throw new KeyNotFoundException($"User with ID {userId} not found") : user.IsModerator;
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<uint> GetUserMaxSubscriptionsAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                var user = _users.FirstOrDefault(u => u.Id == userId);
                return user is null ? throw new KeyNotFoundException($"User with ID {userId} not found") : user.MaxSubscriptions;
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task SetUsersMinIntervalAsync(string userId, uint minInterval)
        {
            await _semaphore.WaitAsync();
            try
            {
                var targetUser = _users.FirstOrDefault(u => u.Id == userId) ?? throw new KeyNotFoundException($"User with ID {userId} not found");
                targetUser.ChangeIntervalLimits(minInterval);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task SetUsersMaxSubscriptionsAsync(string userId, uint MaxSubscriptions)
        {
            await _semaphore.WaitAsync();
            try
            {
                var targetUser = _users.FirstOrDefault(u => u.Id == userId) ?? throw new KeyNotFoundException($"User with ID {userId} not found");
                targetUser.ChangeSubscriptionsLimits(MaxSubscriptions);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task BanUserAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                var targetUser = _users.FirstOrDefault(u => u.Id == userId) ?? throw new KeyNotFoundException($"User with ID {userId} not found");
                targetUser.Block();
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task UnbanUserAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                var targetUser = _users.FirstOrDefault(u => u.Id == userId) ?? throw new KeyNotFoundException($"User with ID {userId} not found");
                targetUser.Unblock();
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task PromoteUserAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                var targetUser = _users.FirstOrDefault(u => u.Id == userId) ?? throw new KeyNotFoundException($"User with ID {userId} not found");
                targetUser.Promote();
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task DemoteUserAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                var targetUser = _users.FirstOrDefault(u => u.Id == userId) ?? throw new KeyNotFoundException($"User with ID {userId} not found");
                targetUser.Demote();
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<bool> IsUserBannedAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                var user = _users.FirstOrDefault(u => u.Id == userId);
                return user is null ? throw new KeyNotFoundException($"User with ID {userId} not found") : user.IsBlocked;
            }
            finally
            {
                _semaphore.Release();
            }
        }
    }

}
