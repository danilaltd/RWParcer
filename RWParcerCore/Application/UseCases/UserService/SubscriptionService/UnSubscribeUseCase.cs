using RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.UserService.SubscriptionService
{
    internal class UnSubscribeUseCase(IUserRepository userRepository, ISubscriptionRepository subscriptionRepository) : IUnSubscribe
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly ISubscriptionRepository _subscriptionRepository = subscriptionRepository;
        public async Task UnSubscribeAsync(string userId, SubscriptionVO subscription)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) return;
            var favorites = await _subscriptionRepository.GetSubscriptionsAsync(userId);

            var favoriteToRemove = favorites.FirstOrDefault(f => f.Subscription.Equals(subscription));

            if (favoriteToRemove == null) return;

            await _subscriptionRepository.RemoveSubscriptionAsync(favoriteToRemove);
        }
    }
}
