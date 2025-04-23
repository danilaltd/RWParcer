using RWParcerCore.Application.Interfaces.IUserService.IFavoritesService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.UserService.FavoritesService
{
    internal class AddToFavoritesUseCase(IUserRepository userRepository, IFavoritesRepository favoriteRepository) : IAddToFavorites
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IFavoritesRepository _favoriteRepository = favoriteRepository;

        public async Task AddToFavoritesAsync(string userId, TrainVO train)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (!await _favoriteRepository.ExistsAsync(userId, train)) throw new InvalidOperationException($"Train {train} already in favorites");

            await _favoriteRepository.AddFavoriteAsync(new FavoriteItem(userId, train));
        }
    }
}
