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

            return [.. (await _subscriptionRepository.GetSubscriptionsAsync(userId)).Select(favorite => favorite.Subscription)];
        }
    }
}
