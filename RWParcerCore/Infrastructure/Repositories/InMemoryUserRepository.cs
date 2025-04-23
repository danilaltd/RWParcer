using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemoryUserRepository : IUserRepository
    {
        private readonly List<User> _users = new();
        private readonly SemaphoreSlim _semaphore = new(1, 1); // Потокобезопасный механизм блокировки

        public async Task<User?> GetUserByIdAsync(string id)
        {
            await _semaphore.WaitAsync();
            try
            {
                return _users.FirstOrDefault(u => u.Id == id);
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

        public async Task<uint> GetUserMinIntervalAsync(string id)
        {
            await _semaphore.WaitAsync();
            try
            {
                return _users.FirstOrDefault(u => u.Id == id)?.MinSubscriptionsInterval ?? throw new Exception("No such user");
            }
            finally
            {
                _semaphore.Release();
            }
        }
    }

}
