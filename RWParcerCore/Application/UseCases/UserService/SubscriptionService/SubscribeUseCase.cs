using RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.UserService.SubscriptionService
{
    internal class SubscribeUseCase : ISubscribe
    {
        private readonly IUserRepository _userRepository;
        private readonly ISubscriptionRepository _subscriptionRepository;
        public SubscribeUseCase(IUserRepository userRepository, ISubscriptionRepository subscriptionRepository)
        {
            _userRepository = userRepository;
            _subscriptionRepository = subscriptionRepository;
        }

        public async Task SubscribeAsync(string userId, SubscriptionVO subscription)
        {
            User? existingUser = await _userRepository.GetUserByIdAsync(userId);
            if (existingUser == null) return;
            if (await _subscriptionRepository.ExistsAsync(userId, subscription)) return;

            await _subscriptionRepository.AddSubscriptionAsync(new SubscriptionItem(userId, subscription, await _userRepository.GetUserMinIntervalAsync(userId)));
        }
    }
}
