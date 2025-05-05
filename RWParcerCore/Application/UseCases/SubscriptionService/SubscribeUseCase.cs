using RWParcerCore.Application.Interfaces.ISubscriptionService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.SubscriptionService
{
    internal class SubscribeUseCase(IUserRepository userRepository, ISubscriptionRepository subscriptionRepository) : ISubscribe
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly ISubscriptionRepository _subscriptionRepository = subscriptionRepository;

        public async Task SubscribeAsync(string userId, SubscriptionVO subscription)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (await _subscriptionRepository.SubscriptionExistsAsync(userId, subscription)) throw new InvalidOperationException($"User {userId} already has this subscription");

            var subscriptionCount = await _subscriptionRepository.GetSubscriptionCountAsync(userId);
            var maxSubscr = await _userRepository.GetUserMaxSubscriptionsAsync(userId);
            if (subscriptionCount >= maxSubscr)
                throw new OverflowException($"User {userId} has reached the subscription limit ({maxSubscr})");

            await _subscriptionRepository.AddAsync(new Subscription(Guid.NewGuid(), userId, subscription));
        }
    }
}
