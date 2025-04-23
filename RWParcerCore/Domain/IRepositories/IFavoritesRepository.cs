using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface IFavoritesRepository
    {
        Task<IEnumerable<FavoriteItem>> GetFavoritesAsync(string userId);
        Task AddFavoriteAsync(FavoriteItem favoriteItem);
        Task RemoveFavoriteAsync(FavoriteItem favoriteItem);
        Task<bool> ExistsAsync(string userId, TrainVO train);
    }

}
