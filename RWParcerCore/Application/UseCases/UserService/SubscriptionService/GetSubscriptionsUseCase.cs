using RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.UserService.SubscriptionService
{
    internal class GetSubscriptionsUseCase(IUserRepository userRepository, ISubscriptionRepository subscriptionRepository) : IGetSubscriptions
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly ISubscriptionRepository _subscriptionRepository = subscriptionRepository;

        public async Task<List<SubscriptionVO>> GetSubscriptionsAsync(string userId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");

            return [.. (await _subscriptionRepository.GetUserSubscriptionsAsync(userId)).Select(favorite => favorite.Details)];
        }
    }
}
