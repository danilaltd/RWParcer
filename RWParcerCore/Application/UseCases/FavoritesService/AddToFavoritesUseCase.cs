using RWParcerCore.Application.Interfaces.IFavoritesService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.FavoritesService
{
    internal class AddToFavoritesUseCase(IUserRepository userRepository, IFavoritesRepository favoriteRepository) : IAddToFavorites
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IFavoritesRepository _favoriteRepository = favoriteRepository;

        public async Task AddToFavoritesAsync(string userId, TrainVO train)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (await _favoriteRepository.FavoriteExistsAsync(userId, train)) throw new InvalidOperationException($"Train {train} already in favorites");

            await _favoriteRepository.AddAsync(new Favorite(Guid.NewGuid(), userId, train));
        }
    }
}
