using RWParcerCore.Application.Interfaces.IUserService.IFavoritesService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.UserService.FavoritesService
{
    internal class RemoveFromFavoritesUseCase : IRemoveFromFavorites
    {
        private readonly IUserRepository _userRepository;
        private readonly IFavoritesRepository _favoriteRepository;
        public RemoveFromFavoritesUseCase(IUserRepository userRepository, IFavoritesRepository favoriteRepository)
        {
            _userRepository = userRepository;
            _favoriteRepository = favoriteRepository;
        }
        public async Task RemoveFromFavoritesAsync(string userId, TrainVO train)
        {
            if (await _userRepository.GetUserByIdAsync(userId) == null) return;
            var favorites = await _favoriteRepository.GetFavoritesAsync(userId);

            var favoriteToRemove = favorites.FirstOrDefault(f => f.Train.Equals(train));

            if (favoriteToRemove == null) return;

            await _favoriteRepository.RemoveFavoriteAsync(favoriteToRemove);
        }
    }
}
