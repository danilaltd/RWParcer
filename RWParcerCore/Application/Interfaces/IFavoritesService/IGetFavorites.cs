using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IFavoritesService
{
    internal interface IGetFavorites
    {
        Task<List<TrainVO>> GetFavoritesAsync(string userId);
    }
}
