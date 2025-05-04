using RWParcerCore.Application.Interfaces.IFavoritesService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.FavoritesService
{
    internal class RemoveFromFavoritesUseCase(IUserRepository userRepository, IFavoritesRepository favoriteRepository) : IRemoveFromFavorites
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IFavoritesRepository _favoriteRepository = favoriteRepository;

        public async Task RemoveFromFavoritesAsync(string userId, TrainVO train)
        {
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            await _userRepository.UpdateActivityAsync(userId);
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");

            var favoriteToRemove = (await _favoriteRepository.GetFavoritesAsync(userId)).FirstOrDefault(f => f.TrainInfo.Equals(train)) ?? throw new KeyNotFoundException($"Favorite item not found {userId}");

            await _favoriteRepository.RemoveAsync(favoriteToRemove);
        }
    }
}
