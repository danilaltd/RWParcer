using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;
using System.Diagnostics;

namespace RWParcerCore.Infrastructure.Repositories
{
    internal class InMemoryFavoritesRepository : IFavoritesRepository
    {
        private readonly List<Favorite> _favorites = [];
        private readonly SemaphoreSlim _semaphore = new(1, 1);

        private readonly object _lock = new();

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

        public async Task AddFavoriteAsync(Favorite favoriteItem)
        {
            if (favoriteItem == null)
            {
                Debug.WriteLine("AddFavorite err");
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
                Debug.WriteLine("Exists err");
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

        public async Task RemoveFavoriteAsync(Favorite favoriteItem)
        {
            if (favoriteItem == null)
            {
                Debug.WriteLine("RemoveFavorite err");
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
