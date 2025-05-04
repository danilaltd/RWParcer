using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class UserRepository : RepositoryBase, IUserRepository
    {
        public UserRepository(IAppDbContextFactory factory)
            : base(factory)
        {
        }

        public Task<bool> IsUserRegistredAsync(string userId)
            => QueryAsync(ctx =>
                ctx.Users.AnyAsync(u => u.Id == userId)
            );

        public Task AddAsync(User user)
        {
            ArgumentNullException.ThrowIfNull(user);
            return ExecuteAsync(async ctx =>
            {
                await ctx.Users.AddAsync(user);
                await ctx.SaveChangesAsync();
            });
        }

        public Task<uint> GetUserMinIntervalAsync(string userId)
            => QueryAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                return u.MinSubscriptionsInterval;
            });

        public Task<bool> IsUserModeratorAsync(string userId)
            => QueryAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                return u.IsModerator;
            });

        public Task<uint> GetUserMaxSubscriptionsAsync(string userId)
            => QueryAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                return u.MaxSubscriptions;
            });

        public Task SetUsersMinIntervalAsync(string userId, uint minInterval)
            => ExecuteAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                u.ChangeIntervalLimits(minInterval);
                await ctx.SaveChangesAsync();
            });

        public Task SetUsersMaxSubscriptionsAsync(string userId, uint maxSubscriptions)
            => ExecuteAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                u.ChangeSubscriptionsLimits(maxSubscriptions);
                await ctx.SaveChangesAsync();
            });

        public Task BanUserAsync(string userId)
            => ExecuteAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                u.Block();
                await ctx.SaveChangesAsync();
            });

        public Task UnbanUserAsync(string userId)
            => ExecuteAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                u.Unblock();
                await ctx.SaveChangesAsync();
            });

        public Task PromoteUserAsync(string userId)
            => ExecuteAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                u.Promote();
                await ctx.SaveChangesAsync();
            });

        public Task DemoteUserAsync(string userId)
            => ExecuteAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                u.Demote();
                await ctx.SaveChangesAsync();
            });

        public Task<bool> IsUserBannedAsync(string userId)
            => QueryAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                return u.IsBlocked;
            });

        public Task UpdateActivityAsync(string userId)
            => ExecuteAsync(async ctx =>
            {
                var u = await ctx.Users.FirstOrDefaultAsync(x => x.Id == userId)
                        ?? throw new KeyNotFoundException($"User {userId} not found");
                u.LastActivity = DateTime.Now;
                await ctx.SaveChangesAsync();
            });

        public Task<List<User>> GetLastUsersAsync(TimeSpan timeSpan)
        {
            var cutoffTime = DateTime.Now.Subtract(timeSpan); // Вычисляем пороговое время перед запросом

            return QueryAsync(ctx =>
                ctx.Users
                   .Where(u => u.LastActivity >= cutoffTime) // Сравниваем с вычисленным значением
                   .ToListAsync());
        }

        public async Task<User> GetUserByIdAsync(string userId)
        {
            var user = await QueryAsync(ctx =>
                ctx.Users.FirstOrDefaultAsync(u => u.Id == userId));
            return user ?? throw new KeyNotFoundException($"User {userId} not found.");
        }



    }
}
