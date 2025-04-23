using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService
{
    internal class SetUsersMaxSubscriptionsUseCase(IUserRepository userRepository) : ISetUsersMaxSubscriptions
    {
        private readonly IUserRepository _userRepository = userRepository;

        public async Task SetUsersMaxSubscriptionsAsync(string userId, string targetId, uint maxSubscriptions)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (!await _userRepository.IsUserModeratorAsync(userId)) throw new UnauthorizedAccessException($"Only moderators can ban users {userId}");
            if (!await _userRepository.IsUserRegistredAsync(targetId)) throw new KeyNotFoundException($"User with ID {targetId} not found");

            await _userRepository.SetUsersMaxSubscriptionsAsync(targetId, maxSubscriptions);
        }
    }
}
