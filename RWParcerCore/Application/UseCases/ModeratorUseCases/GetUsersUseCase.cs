using RWParcerCore.Application.Interfaces.IModerator;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.Mappers;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.ModeratorUseCases
{
    internal class GetUsersUseCase(IUserRepository userRepository) : IGetUsers
    {
        private readonly IUserRepository _userRepository = userRepository;

        public async Task<List<UserVO>> GetUsersAsync(string userId, TimeSpan timeSpan)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (!await _userRepository.IsUserModeratorAsync(userId)) throw new UnauthorizedAccessException($"Only moderators can get users {userId}");
            return [.. (await _userRepository.GetLastUsersAsync(timeSpan)).Select(item => UserMapper.FromEntity(item))];
        }
    }
}
