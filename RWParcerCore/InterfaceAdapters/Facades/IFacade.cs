using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.InterfaceAdapters.Facades
{
    public interface IFacade
    {
        Task AddToFavoritesAsync(string userId, TrainVO train);
        Task<bool> IsInFavoritesAsync(string userId, TrainVO train);
        Task AuthenticateUser(string userId);
        Task BanUserAsync(string userId, string targetId);
        Task DemoteUserAsync(string userId, string targetId);
        Task<List<TrainVO>> GetFavoritesAsync(string userId);
        Task<List<MessageVO>> GetMessagesAsync(string userId);
        Task<List<MessageVO>> GetAllMessagesAsync(string userId);
        Task<List<StationVO>> GetStationAsync(string userId, string prefix);
        Task<List<SubscriptionVO>> GetSubscritionsAsync(string userId, string targetId);
        Task<List<TrainVO>> GetTimesForRouteAsync(string userId, RouteVO route);
        Task<List<UserVO>> GetUsersAsync(string userId, TimeSpan timeSpan);
        Task<bool> IsUserModeratorAsync(string userId, string targetId);
        Task<List<NotificationVO>> PopNotificationsAsync();
        Task PromoteUserAsync(string userId, string targetId);
        Task RemoveFromFavoritesAsync(string userId, TrainVO train);
        Task SendFeedbackAsync(string userId, string message);
        Task SendMessageAsync(string userId, string targetId, string message);
        Task SetUsersMaxSubscriptionsAsync(string userId, string targetId, uint maxSubscriptions);
        Task SetUsersMinIntervalAsync(string userId, string targetId, uint maxSubscriptions);
        Task StopAsync();
        Task SubscribeAsync(string userId, SubscriptionVO subscription);
        Task UnbanUserAsync(string userId, string targetId);
        Task UnSubscribeAsync(string userId, SubscriptionVO subscription);
        Task ResetSubscribeAsync(string userId, SubscriptionVO subscription);
        Task<bool> IsUserBannedAsync(string userId, string targetId);
        Task<UserVO> GetUserByIdAsync(string userId, string targetId);
    }
}