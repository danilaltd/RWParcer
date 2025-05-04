using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IFavoritesService
{
    internal interface IIsInFavorites
    {
        public Task<bool> IsInFavoritesAsync(string userId, TrainVO train);
    }
}
