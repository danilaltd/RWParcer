using RWParcerCore.Domain.Interfaces;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemoryFavoritesRepository(ILogger logger) : IFavoritesRepository
    {
        private readonly List<Favorite> _favorites = [];
        private readonly SemaphoreSlim _semaphore = new(1, 1);
        private readonly ILogger _logger = logger;

        public async Task<IEnumerable<Favorite>> GetFavoritesAsync(string userId)
        {
            await _semaphore.WaitAsync();
            try
            {
                return [.. _favorites.Where(f => f.UserId == userId)];
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task AddAsync(Favorite favoriteItem)
        {
            if (favoriteItem == null)
            {
                _logger.LogDebug("AddFavorite err");
                return;
            }

            await _semaphore.WaitAsync();
            try
            {
                _favorites.Add(favoriteItem);
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task<bool> FavoriteExistsAsync(string userId, TrainVO train)
        {
            if (train is null)
            {
                _logger.LogDebug("Exists err");
                return false;
            }

            await _semaphore.WaitAsync();
            try
            {
                return _favorites.Any(f => f.UserId == userId && f.TrainInfo.Equals(train));
            }
            finally
            {
                _semaphore.Release();
            }
        }

        public async Task RemoveAsync(Favorite favoriteItem)
        {
            if (favoriteItem == null)
            {
                _logger.LogDebug("RemoveFavorite err");
                return;
            }

            await _semaphore.WaitAsync();
            try
            {
                _favorites.Remove(favoriteItem);
            }
            finally
            {
                _semaphore.Release();
            }
        }
    }
}
