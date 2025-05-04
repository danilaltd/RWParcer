using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IFavoritesService
{
    internal interface IRemoveFromFavorites
    {
        Task RemoveFromFavoritesAsync(string userId, TrainVO train);
    }
}
