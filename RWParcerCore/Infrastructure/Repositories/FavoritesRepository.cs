using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;
using System.Diagnostics;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class FavoritesRepository : RepositoryBase, IFavoritesRepository
    {
        public FavoritesRepository(IAppDbContextFactory factory)
            : base(factory)
        {
        }

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
                Debug.WriteLine("AddFavorite err");
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
                Debug.WriteLine("Exists err");
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
                Debug.WriteLine("RemoveFavorite err");
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
