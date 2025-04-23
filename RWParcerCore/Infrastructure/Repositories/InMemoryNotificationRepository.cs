using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemoryNotificationRepository : INotificationRepository
    {
        private readonly List<NotificationItem> _notifications = new();
        private readonly SemaphoreSlim _semaphore = new(1, 1);

        public async Task<IEnumerable<NotificationItem>> PopNotificationsAsync()
        {
            await _semaphore.WaitAsync();
            try
            {
                var userNotifications = new List<NotificationItem>(_notifications);
                _notifications.Clear();
                return userNotifications;
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task AddNotificationAsync(NotificationItem notificationItem)
        {
            if (notificationItem == null)
                throw new ArgumentNullException(nameof(notificationItem));

            await _semaphore.WaitAsync();
            try
            {
                _notifications.Add(notificationItem);
            }
            finally
            {
                _semaphore.Release();
            }
        }
    }

}
