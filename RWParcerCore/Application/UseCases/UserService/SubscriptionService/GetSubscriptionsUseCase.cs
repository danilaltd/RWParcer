using RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.UserService.SubscriptionService
{
    internal class GetSubscriptionsUseCase : IGetSubscriptions
    {
        private readonly IUserRepository _userRepository;
        private readonly ISubscriptionRepository _subscriptionRepository;
        public GetSubscriptionsUseCase(IUserRepository userRepository, ISubscriptionRepository subscriptionRepository)
        {
            _userRepository = userRepository;
            _subscriptionRepository = subscriptionRepository;
        }

        public async Task<List<SubscriptionVO>> GetSubscriptionsAsync(string userId)
        {
            if (await _userRepository.GetUserByIdAsync(userId) == null) return [];

            var favorites = await _subscriptionRepository.GetSubscriptionsAsync(userId);

            return favorites.Select(favorite => favorite.Subscription).ToList();
        }
    }
}
