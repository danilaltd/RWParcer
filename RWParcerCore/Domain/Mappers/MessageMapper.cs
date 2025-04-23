using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.Mappers
{
    internal static class MessageMapper
    {
        public static MessageVO FromEntity(Message message) => new(
            senderId: message.SenderId,
            receiverId: message.ReceiverId,
            content: message.Content,
            sentDate: message.SentDate
        );
    }
}
