using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService
{
    internal class SetUsersMinIntervalUseCase(IUserRepository userRepository) : ISetUsersMinInterval
    {
        private readonly IUserRepository _userRepository = userRepository;

        public async Task SetUsersMinIntervalAsync(string userId, string targetId, uint minInterval)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (!await _userRepository.GetUserIsModeratorAsync(userId)) throw new UnauthorizedAccessException("Only moderators can ban users");
            if (!await _userRepository.IsUserRegistredAsync(targetId)) throw new KeyNotFoundException($"User with ID {targetId} not found");

            await _userRepository.SetUsersMinIntervalAsync(targetId, minInterval);
        }
    }
}
