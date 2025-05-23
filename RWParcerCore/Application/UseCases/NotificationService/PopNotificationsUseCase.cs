using RWParcerCore.Application.Interfaces.INotificationService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.Mappers;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.NotificationService
{

    internal class PopNotificationsUseCase(INotificationRepository notificationRepository, IUserRepository userRepository) : IPopNotifications
    {
        private readonly INotificationRepository _notificationRepository = notificationRepository;
        private readonly IUserRepository _userRepository = userRepository;
        public async Task<List<NotificationVO>> PopNotifications()
        {
            var notifications = await _notificationRepository.PopNotificationsAsync();

            var filteredNotifications = new List<NotificationVO>();
            foreach (var item in notifications)
            {
                if (!await _userRepository.IsUserBannedAsync(item.UserId))
                {
                    filteredNotifications.Add(NotificationMapper.FromEntity(item));
                }
            }

            return filteredNotifications;
        }
    }
}
