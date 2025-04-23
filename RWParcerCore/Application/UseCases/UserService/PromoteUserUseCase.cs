using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService
{
    internal class PromoteUserUseCase(IUserRepository userRepository) : IPromoteUser
    {
        private readonly IUserRepository _userRepository = userRepository;

        public async Task PromoteUserAsync(string userId, string targetId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (!await _userRepository.IsUserModeratorAsync(userId)) throw new UnauthorizedAccessException($"Only moderators can promote users {userId}");
            if (!await _userRepository.IsUserRegistredAsync(targetId)) throw new KeyNotFoundException($"User with ID {targetId} not found");

            await _userRepository.PromoteUserAsync(targetId);
        }
    }
}
