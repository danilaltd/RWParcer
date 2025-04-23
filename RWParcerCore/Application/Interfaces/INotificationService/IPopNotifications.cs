using RWParcerCore.Domain.Entities;

namespace RWParcerCore.Application.Interfaces.INotificationService
{
    internal interface IPopNotifications
    {
        Task<List<NotificationItem>> PopNotifications();
    }
}
