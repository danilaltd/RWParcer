using RWParcerCore.Domain.Entities;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface IMessageRepository
    {
        Task AddMessageAsync(Message message);
        Task<IEnumerable<Message>> GetMessagesAsync(string userId);
        Task<IEnumerable<Message>> GetAllMessagesAsync();
    }
}
