using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService
{
    internal class GetUserStatusUseCase(IUserRepository userRepository) : IGetUserStatus
    {
        private readonly IUserRepository _userRepository = userRepository;
        public async Task<string> GetUserStatusAsync(string userId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");

            var details = new List<string>
            {
                (await _userRepository.IsUserModeratorAsync(userId)) ? "Вы модератор" : "",
                $"Минимальный интервал обновления: {(await _userRepository.GetUserMinIntervalAsync(userId))}",
                $"Максимальное количество подписок: {(await _userRepository.GetUserMaxSubscriptionsAsync(userId))}"
            };
            return string.Join("\n", details.Where(line => !string.IsNullOrEmpty(line)));
        }
    }
}
