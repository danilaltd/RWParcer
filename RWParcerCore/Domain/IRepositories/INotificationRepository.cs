using RWParcerCore.Domain.Entities;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface INotificationRepository
    {
        Task<IEnumerable<Notification>> PopNotificationsAsync();
        Task AddAsync(Notification notificationItem);
    }
}
