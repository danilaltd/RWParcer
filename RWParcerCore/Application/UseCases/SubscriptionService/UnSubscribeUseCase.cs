using RWParcerCore.Application.Interfaces.ISubscriptionService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.SubscriptionService
{
    internal class UnSubscribeUseCase(IUserRepository userRepository, ISubscriptionRepository subscriptionRepository) : IUnSubscribe
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly ISubscriptionRepository _subscriptionRepository = subscriptionRepository;
        public async Task UnSubscribeAsync(string userId, SubscriptionVO subscription)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            var subscriptions = await _subscriptionRepository.GetUserSubscriptionsAsync(userId);

            var subscriptionToRemove = subscriptions.FirstOrDefault(f => f.Details.Equals(subscription));

            if (subscriptionToRemove == null) throw new InvalidOperationException($"{userId} No such subscription");

            await _subscriptionRepository.RemoveAsync(subscriptionToRemove);
        }
    }
}
