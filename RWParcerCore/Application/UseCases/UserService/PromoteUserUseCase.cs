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
            if (!await _userRepository.GetUserIsModeratorAsync(userId)) throw new UnauthorizedAccessException("Only moderators can promote users");
            if (!await _userRepository.IsUserRegistredAsync(targetId)) throw new KeyNotFoundException($"User with ID {targetId} not found");

            await _userRepository.PromoteUserAsync(targetId);
        }
    }
}
