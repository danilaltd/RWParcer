using RWParcerCore.Application.Interfaces;
using RWParcerCore.Application.Interfaces.IUserService.IFavoritesService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;
using System.Diagnostics;

namespace RWParcerCore.Application.UseCases.UserService.FavoritesService
{
    internal class GetFavoritesUseCase : IGetFavorites
    {
        private readonly IUserRepository _userRepository;
        private readonly IFavoritesRepository _favoriteRepository;
        public GetFavoritesUseCase(IUserRepository userRepository, IFavoritesRepository favoriteRepository)
        {
            _userRepository = userRepository;
            _favoriteRepository = favoriteRepository;
        }

        public async Task<List<TrainVO>> GetFavoritesAsync(string userId)
        {
            if (await _userRepository.GetUserByIdAsync(userId) == null) return [];

            var favorites = await _favoriteRepository.GetFavoritesAsync(userId);

            return favorites.Select(favorite => favorite.Train).ToList();
        }
    }
}
