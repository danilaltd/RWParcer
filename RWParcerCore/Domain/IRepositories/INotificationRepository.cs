using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface INotificationRepository
    {
        Task<IEnumerable<NotificationItem>> PopNotificationsAsync();
        Task AddNotificationAsync(NotificationItem notificationItem);
    }
}
