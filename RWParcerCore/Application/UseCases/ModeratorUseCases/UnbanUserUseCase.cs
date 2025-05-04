using RWParcerCore.Application.Interfaces.IModerator;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.ModeratorUseCases
{
    internal class UnbanUserUseCase(IUserRepository userRepository) : IUnbanUser
    {
        private readonly IUserRepository _userRepository = userRepository;

        public async Task UnbanUserAsync(string userId, string targetId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (!await _userRepository.IsUserModeratorAsync(userId)) throw new UnauthorizedAccessException($"Only moderators can unban users {userId}");
            if (!await _userRepository.IsUserRegistredAsync(targetId)) throw new KeyNotFoundException($"User with ID {targetId} not found");

            await _userRepository.UnbanUserAsync(targetId);
        }
    }
}
