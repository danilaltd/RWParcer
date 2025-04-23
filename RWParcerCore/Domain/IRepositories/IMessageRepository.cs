using RWParcerCore.Domain.Entities;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface IMessageRepository
    {
        void Add(Message message);
        Message GetById(Guid messageId);
        //IList<Message> GetUnreadMessagesByReceiver(Guid receiverId);
        //IList<Message> GetMessagesByModerator(Guid moderatorId);
    }

}
