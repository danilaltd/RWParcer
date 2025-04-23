using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IUserService.IFavoritesService
{
    internal interface IGetFavorites
    {
        Task<List<TrainVO>> GetFavoritesAsync(string userId);
    }
}
