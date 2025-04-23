using RWParcerCore.Application.Interfaces.INotificationService;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.Mappers;

namespace RWParcerCore.Application.UseCases.NotificationService
{

    internal class PopNotificationsUseCase(INotificationRepository notificationRepository) : IPopNotifications
    {
        private readonly INotificationRepository _notificationRepository = notificationRepository;
        public async Task<List<NotificationVO>> PopNotifications()
        {
            return [.. (await _notificationRepository.PopNotificationsAsync()).Select(item => NotificationMapper.FromEntity(item))];
        }
    }
}
