using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService
{
    internal class UnbanUserUseCase(IUserRepository userRepository) : IUnbanUser
    {
        private readonly IUserRepository _userRepository = userRepository;

        public async Task UnbanUserAsync(string userId, string targetId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (!await _userRepository.GetUserIsModeratorAsync(userId)) throw new UnauthorizedAccessException("Only moderators can unban users");
            if (!await _userRepository.IsUserRegistredAsync(targetId)) throw new KeyNotFoundException($"User with ID {targetId} not found");

            await _userRepository.UnbanUserAsync(targetId);
        }
    }
}
