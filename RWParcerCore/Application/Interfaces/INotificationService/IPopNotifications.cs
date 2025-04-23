using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.INotificationService
{
    internal interface IPopNotifications
    {
        Task<List<NotificationVO>> PopNotifications();
    }
}
