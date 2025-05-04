using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemoryMessageRepository : IMessageRepository
    {
        private readonly List<Message> _messages = [];
        private readonly SemaphoreSlim _semaphore = new(1, 1);

        public async Task AddAsync(Message message)
        {
            ArgumentNullException.ThrowIfNull(message);

            await _semaphore.WaitAsync();
            try
            {
                _messages.Add(message);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<IEnumerable<Message>> GetAllMessagesAsync()
        {
            await _semaphore.WaitAsync();
            try
            {
                var messages = new List<Message>(_messages);
                return messages;
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<IEnumerable<Message>> GetUserMessagesAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                var messages = _messages.Where(msg => msg.ReceiverId == userId);
                return messages;
            }
            finally
            {
                _semaphore.Release();
            }
        }
    }
}
