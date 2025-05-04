using RWParcerCore.Application.Interfaces.ISubscriptionService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.SubscriptionService
{
    internal class GetSubscriptionsUseCase(IUserRepository userRepository, ISubscriptionRepository subscriptionRepository) : IGetSubscriptions
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly ISubscriptionRepository _subscriptionRepository = subscriptionRepository;

        public async Task<List<SubscriptionVO>> GetSubscriptionsAsync(string userId, string targetId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (userId == targetId || await _userRepository.IsUserModeratorAsync(userId))
                return [.. (await _subscriptionRepository.GetUserSubscriptionsAsync(targetId)).Select(favorite => favorite.Details)];
            else throw new UnauthorizedAccessException($"{userId} tries get {targetId} subscriptions when not moder");
        }
    }
}
