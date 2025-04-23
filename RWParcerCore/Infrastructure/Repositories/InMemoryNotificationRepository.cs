using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemoryNotificationRepository : INotificationRepository
    {
        private readonly List<Notification> _notifications = [];
        private readonly SemaphoreSlim _semaphore = new(1, 1);

        public async Task<IEnumerable<Notification>> PopNotificationsAsync()
        {
            await _semaphore.WaitAsync();
            try
            {
                var userNotifications = new List<Notification>(_notifications);
                _notifications.Clear();
                return userNotifications;
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task AddNotificationAsync(Notification notificationItem)
        {
            ArgumentNullException.ThrowIfNull(notificationItem);

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
