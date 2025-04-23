using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.Mappers
{
    internal static class NotificationMapper
    {
        public static NotificationVO FromEntity(Notification notification) => new(
            userId: notification.UserId,
            content: notification.Content
        );
    }
}
