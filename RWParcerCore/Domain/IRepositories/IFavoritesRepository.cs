using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface IFavoritesRepository
    {
        Task<IEnumerable<Favorite>> GetFavoritesAsync(string userId);
        Task AddFavoriteAsync(Favorite favoriteItem);
        Task RemoveFavoriteAsync(Favorite favoriteItem);
        Task<bool> FavoriteExistsAsync(string userId, TrainVO train);
    }

}
