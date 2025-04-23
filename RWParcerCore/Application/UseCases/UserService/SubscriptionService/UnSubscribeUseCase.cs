using RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.UserService.SubscriptionService
{
    internal class UnSubscribeUseCase : IUnSubscribe
    {
        private readonly IUserRepository _userRepository;
        private readonly ISubscriptionRepository _subscriptionRepository;
        public UnSubscribeUseCase(IUserRepository userRepository, ISubscriptionRepository subscriptionRepository)
        {
            _userRepository = userRepository;
            _subscriptionRepository = subscriptionRepository;
        }
        public async Task UnSubscribeAsync(string userId, SubscriptionVO subscription)
        {
            if (await _userRepository.GetUserByIdAsync(userId) == null) return;
            var favorites = await _subscriptionRepository.GetSubscriptionsAsync(userId);

            var favoriteToRemove = favorites.FirstOrDefault(f => f.Subscription.Equals(subscription));

            if (favoriteToRemove == null) return;

            await _subscriptionRepository.RemoveSubscriptionAsync(favoriteToRemove);
        }
    }
}
