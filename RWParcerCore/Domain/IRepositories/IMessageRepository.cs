using RWParcerCore.Domain.Entities;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface IMessageRepository
    {
        Task AddAsync(Message message);
        Task<IEnumerable<Message>> GetUserMessagesAsync(string userId);
        Task<IEnumerable<Message>> GetAllMessagesAsync();
    }
}
