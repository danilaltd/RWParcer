using RWParcerCore.Application.Interfaces.IUserService.IFavoritesService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;
using System.Threading.Tasks;

namespace RWParcerCore.Application.UseCases.UserService.FavoritesService
{
    internal class AddToFavoritesUseCase : IAddToFavorites
    {
        private readonly IUserRepository _userRepository;
        private readonly IFavoritesRepository _favoriteRepository;
        public AddToFavoritesUseCase(IUserRepository userRepository, IFavoritesRepository favoriteRepository)
        {
            _userRepository = userRepository;
            _favoriteRepository = favoriteRepository;
        }
        public async Task AddToFavoritesAsync(string userId, TrainVO train)
        {
            User? existingUser = await _userRepository.GetUserByIdAsync(userId);
            if (existingUser == null) return;
            if (await _favoriteRepository.ExistsAsync(userId, train)) return;

            await _favoriteRepository.AddFavoriteAsync(new FavoriteItem(userId, train));
        }
    }
}
