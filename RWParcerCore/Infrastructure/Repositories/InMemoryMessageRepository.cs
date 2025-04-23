using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemoryMessageRepository : IMessageRepository
    {
        private readonly List<Message> _messages = [];

        public void Add(Message message)
        {
            _messages.Add(message);
        }

        public Message GetById(Guid messageId)
        {
            return _messages.FirstOrDefault(m => m.Id == messageId);
        }

        //public IList<Message> GetUnreadMessagesByReceiver(Guid receiverId)
        //{
            //return _messages.Where(m => m.Receiver.Id == receiverId && !m.IsRead).ToList();
        //}

        //public IList<Message> GetMessagesByModerator(Guid moderatorId)
        //{
            // Предположим, что сообщения для модератора — это сообщения, полученные модераторами,
            // либо с дополнительной логикой фильтрации
            //return _messages.Where(m => m.Receiver.Id == moderatorId).ToList();
        //}
    }
}
