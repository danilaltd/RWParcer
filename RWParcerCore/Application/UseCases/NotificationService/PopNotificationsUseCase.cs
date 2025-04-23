using RWParcerCore.Application.Interfaces.INotificationService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.NotificationService
{

    internal class PopNotificationsUseCase : IPopNotifications
    {
        private readonly INotificationRepository _notificationRepository;

        public PopNotificationsUseCase(INotificationRepository notificationRepository) => _notificationRepository = notificationRepository;

        public async Task<List<NotificationItem>> PopNotifications()
        {
            return [.. await _notificationRepository.PopNotificationsAsync()];
        }
    }
}
