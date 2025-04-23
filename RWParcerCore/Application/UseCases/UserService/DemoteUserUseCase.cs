using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService
{
    internal class DemoteUserUseCase(IUserRepository userRepository) : IDemoteUser
    {
        private readonly IUserRepository _userRepository = userRepository;

        public async Task DemoteUserAsync(string userId, string targetId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (!await _userRepository.GetUserIsModeratorAsync(userId)) throw new UnauthorizedAccessException("Only moderators can demote users");
            if (!await _userRepository.IsUserRegistredAsync(targetId)) throw new KeyNotFoundException($"User with ID {targetId} not found");

            await _userRepository.DemoteUserAsync(targetId);
        }
    }
}
