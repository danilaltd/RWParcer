using RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.UserService.SubscriptionService
{
    internal class SubscribeUseCase(IUserRepository userRepository, ISubscriptionRepository subscriptionRepository) : ISubscribe
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly ISubscriptionRepository _subscriptionRepository = subscriptionRepository;

        public async Task SubscribeAsync(string userId, SubscriptionVO subscription)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (await _subscriptionRepository.ExistsAsync(userId, subscription)) throw new InvalidOperationException("User already has this subscription");

            await _subscriptionRepository.AddSubscriptionAsync(new SubscriptionItem(userId, subscription, await _userRepository.GetUserMinIntervalAsync(userId)));
        }
    }
}
