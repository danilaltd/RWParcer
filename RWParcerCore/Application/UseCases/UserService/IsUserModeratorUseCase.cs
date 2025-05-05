using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService
{
    internal class IsUserModeratorUseCase(IUserRepository userRepository) : IIsUserModerator
    {
        private readonly IUserRepository _userRepository = userRepository;
        public async Task<bool> IsUserModeratorAsync(string userId, string targetId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            try
            {
                if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");

                if (userId != targetId)
                {
                    if (!await _userRepository.IsUserModeratorAsync(userId)) throw new UnauthorizedAccessException($"{userId} tries get {targetId} status when not moder");
                    if (!await _userRepository.IsUserRegistredAsync(targetId)) throw new KeyNotFoundException($"User with ID {targetId} not found");
                }
                return await _userRepository.IsUserModeratorAsync(targetId);
            }
            finally
            {
                try
                {
                    await _userRepository.UpdateActivityAsync(userId);
                }
                catch { }
            }
        }
    }
}
