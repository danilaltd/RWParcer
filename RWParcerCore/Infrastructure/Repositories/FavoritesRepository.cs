using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.Interfaces;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class FavoritesRepository(IAppDbContextFactory factory, ILogger logger) : RepositoryBase(factory), IFavoritesRepository
    {
        private readonly ILogger _logger = logger;

        public Task<IEnumerable<Favorite>> GetFavoritesAsync(string userId)
            => QueryAsync(async ctx =>
                (IEnumerable<Favorite>)await ctx.Favorites
                    .Where(f => f.UserId == userId)
                    .ToListAsync()
            );

        public Task AddAsync(Favorite favoriteItem)
        {
            if (favoriteItem is null)
            {
                _logger.LogDebug("AddFavorite err");
                return Task.CompletedTask;
            }

            return ExecuteAsync(async ctx =>
            {
                await ctx.Favorites.AddAsync(favoriteItem);
                await ctx.SaveChangesAsync();
            });
        }

        public Task<bool> FavoriteExistsAsync(string userId, TrainVO train)
        {
            if (train is null)
            {
                _logger.LogDebug("Exists err");
                return Task.FromResult(false);
            }

            return QueryAsync(ctx =>
                ctx.Favorites.AnyAsync(f =>
                    f.UserId == userId &&
                    f.TrainInfo.Equals(train)
                )
            );
        }

        public Task RemoveAsync(Favorite favoriteItem)
        {
            if (favoriteItem == null)
            {
                _logger.LogDebug("RemoveFavorite err");
                return Task.CompletedTask;
            }

            return ExecuteAsync(async ctx =>
            {
                ctx.Favorites.Remove(favoriteItem);
                await ctx.SaveChangesAsync();
            });
        }
    }
}
