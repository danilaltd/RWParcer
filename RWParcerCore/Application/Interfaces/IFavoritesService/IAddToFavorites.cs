using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IFavoritesService
{
    internal interface IAddToFavorites
    {
        public Task AddToFavoritesAsync(string userId, TrainVO train);
    }
}
