using RWParcerCore.Application.Interfaces.IUserService.IModerator;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService.ModeratorUseCases
{
    internal class SetUsersMinIntervalUseCase(IUserRepository userRepository) : ISetUsersMinInterval
    {
        private readonly IUserRepository _userRepository = userRepository;

        public async Task SetUsersMinIntervalAsync(string userId, string targetId, uint minInterval)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (!await _userRepository.IsUserModeratorAsync(userId)) throw new UnauthorizedAccessException($"Only moderators can ban users {userId}");
            if (!await _userRepository.IsUserRegistredAsync(targetId)) throw new KeyNotFoundException($"User with ID {targetId} not found");

            await _userRepository.SetUsersMinIntervalAsync(targetId, minInterval);
        }
    }
}
