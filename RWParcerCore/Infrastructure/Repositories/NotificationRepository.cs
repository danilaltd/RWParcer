using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class NotificationRepository(IAppDbContextFactory factory) : RepositoryBase(factory), INotificationRepository
    {
        public Task<IEnumerable<Notification>> PopNotificationsAsync()
            => QueryAsync(async ctx =>
            {
                var list = await ctx.Notifications.ToListAsync();
                ctx.Notifications.RemoveRange(list);
                await ctx.SaveChangesAsync();
                return (IEnumerable<Notification>)list;
            });

        public Task AddAsync(Notification notificationItem)
        {
            ArgumentNullException.ThrowIfNull(notificationItem);
            return ExecuteAsync(async ctx =>
            {
                await ctx.Notifications.AddAsync(notificationItem);
                await ctx.SaveChangesAsync();
            });
        }
    }
}
