using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.IRepositories
{
    internal interface IFavoritesRepository
    {
        Task<IEnumerable<Favorite>> GetFavoritesAsync(string userId);
        Task AddAsync(Favorite favoriteItem);
        Task RemoveAsync(Favorite favoriteItem);
        Task<bool> FavoriteExistsAsync(string userId, TrainVO train);
    }

}
