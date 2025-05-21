using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.Interfaces;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class SubscriptionRepository : RepositoryBase, ISubscriptionRepository
    {
        public SubscriptionRepository(IAppDbContextFactory factory, ILogger logger)
            : base(factory)
        {
            _logger = logger;
        }
        private readonly ILogger _logger;

        public Task<IEnumerable<Subscription>> GetUserSubscriptionsAsync(string userId)
        {
            return QueryAsync(ctx =>
                ctx.Subscriptions
                   .Where(s => s.UserId == userId)
                   .ToListAsync()
                   .ContinueWith(t => (IEnumerable<Subscription>)t.Result)
            );
        }

        public Task AddAsync(Subscription subscriptionItem)
        {
            if (subscriptionItem == null)
            {
                _logger.LogDebug("AddSubscription err");
                return Task.CompletedTask;
            }

            return ExecuteAsync(async ctx =>
            {
                await ctx.Subscriptions.AddAsync(subscriptionItem);
                await ctx.SaveChangesAsync();
            });
        }

        public Task<bool> SubscriptionExistsAsync(string userId, SubscriptionVO subscription)
        {
            if (subscription is null)
            {
                _logger.LogDebug("Exists err");
                return Task.FromResult(false);
            }

            return QueryAsync(ctx =>
                ctx.Subscriptions
                   .AnyAsync(s => s.UserId == userId && s.Details.Equals(subscription))
            );
        }

        public Task RemoveAsync(Subscription subscriptionItem)
        {
            if (subscriptionItem == null)
            {
                _logger.LogDebug("RemoveSubscription err");
                return Task.CompletedTask;
            }

            return ExecuteAsync(async ctx =>
            {
                ctx.Subscriptions.Remove(subscriptionItem);
                await ctx.SaveChangesAsync();
            });
        }

        public Task<IEnumerable<Subscription>> GetAllSubscriptionsAsync()
        {
            return QueryAsync(ctx =>
                ctx.Subscriptions
                   .ToListAsync()
                   .ContinueWith(t => (IEnumerable<Subscription>)t.Result)
            );
        }

        public Task<uint> GetSubscriptionCountAsync(string userId)
        {
            return QueryAsync(ctx =>
                ctx.Subscriptions
                   .Where(s => s.UserId == userId)
                   .CountAsync()
                   .ContinueWith(t => (uint)t.Result)
            );
        }

        public Task UpdateAsync(Subscription subscription)
        {
            return QueryAsync(ctx =>
                ctx.Subscriptions
                   .Where(s => s.Id == subscription.Id)
                   .ExecuteUpdateAsync(setters => setters
                       .SetProperty(s => s.UserId, subscription.UserId)
                       .SetProperty(s => s.LastUpdate, subscription.LastUpdate)
                       .SetProperty(s => s.LastState, subscription.LastState)
                       .SetProperty(s => s.Details, subscription.Details)
                   )
    );
        }
    }
}
