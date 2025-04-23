using RWParcerCore.Application.Interfaces.IUserService.IFavoritesService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;
using System.Diagnostics;

namespace RWParcerCore.Application.UseCases.UserService.FavoritesService
{
    internal class GetFavoritesUseCase(IUserRepository userRepository, IFavoritesRepository favoriteRepository) : IGetFavorites
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IFavoritesRepository _favoriteRepository = favoriteRepository;

        public async Task<List<TrainVO>> GetFavoritesAsync(string userId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");

            return [.. (await _favoriteRepository.GetFavoritesAsync(userId)).Select(favorite => favorite.Train)];
        }
    }
}
