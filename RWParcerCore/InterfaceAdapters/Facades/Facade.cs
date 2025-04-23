using RWParcerCore.Application.Interfaces.INotificationService;
using RWParcerCore.Application.Interfaces.IRWService;
using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Application.Interfaces.IUserService.IFavoritesService;
using RWParcerCore.Application.Interfaces.IUserService.IModerator;
using RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService;
using RWParcerCore.Application.UseCases.NotificationService;
using RWParcerCore.Application.UseCases.RWService;
using RWParcerCore.Application.UseCases.UserService;
using RWParcerCore.Application.UseCases.UserService.FavoritesService;
using RWParcerCore.Application.UseCases.UserService.FeedbackService;
using RWParcerCore.Application.UseCases.UserService.ModeratorUseCases;
using RWParcerCore.Application.UseCases.UserService.SubscriptionService;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.IServices;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.Infrastructure.Repositories;
using RWParcerCore.Infrastructure.Services;

namespace RWParcerCore.InterfaceAdapters.Facades
{
    public class Facade
    {
        private readonly CancellationTokenSource _cts;
        private readonly INotificationBackgroundService _notificationBackgroundService;

        private readonly IRegisterUser _registerUser;
        private readonly IBanUser _banUser;
        private readonly IUnbanUser _unbanUser;
        private readonly IPromoteUser _promoteUser;
        private readonly IDemoteUser _demoteUser;
        private readonly IGetUserStatus _getUserStatus;
        private readonly ISetUsersMaxSubscriptions _setUsersMaxSubscriptions;
        private readonly ISetUsersMinInterval _setUsersMinInterval;
        private readonly IGetUsers _getUsers;

        private readonly ISendFeedback _sendFeedback;
        private readonly ISendMessage _sendMessage;
        private readonly IGetMessages _getMessages;

        private readonly IGetStations _getStations;
        private readonly IGetTrains _getTrains;

        private readonly IAddToFavorites _addToFavorites;
        private readonly IRemoveFromFavorites _removeFromFavorites;
        private readonly IGetFavorites _getFavorites;

        private readonly ISubscribe _subscribe;
        private readonly IUnSubscribe _unSubscribe;
        private readonly IGetSubscriptions _getSubscriptions;

        private readonly IPopNotifications _popNotifications;
        

        public Facade()
        {
            HttpClient httpClient = new();
            
            IUserRepository userRepository = new InMemoryUserRepository();
            IFavoritesRepository favoritesRepository = new InMemoryFavoritesRepository();
            ISubscriptionRepository subscriptionRepository = new InMemorySubscriptionRepository();
            INotificationRepository notificationRepository = new InMemoryNotificationRepository(); 
            IRWRepository rwRepository = new RWParcer(httpClient);
            IMessageRepository messageRepository = new InMemoryMessageRepository();

            _notificationBackgroundService = new NotificationBackgroundService(subscriptionRepository, notificationRepository, rwRepository, 5, 15); ;
            _cts = new CancellationTokenSource();

            _registerUser = new RegisterUserUseCase(userRepository);
            _banUser = new BanUserUseCase(userRepository);
            _unbanUser = new UnbanUserUseCase(userRepository);
            _promoteUser = new PromoteUserUseCase(userRepository);
            _demoteUser = new DemoteUserUseCase(userRepository);
            _getUserStatus = new GetUserStatusUseCase(userRepository);
            _setUsersMaxSubscriptions = new SetUsersMaxSubscriptionsUseCase(userRepository);
            _setUsersMinInterval = new SetUsersMinIntervalUseCase(userRepository);
            _getUsers = new GetUsersUseCase(userRepository);

            _sendFeedback = new SendFeedbackUseCase(userRepository, messageRepository);
            _sendMessage = new SendMessageUseCase(userRepository, messageRepository, notificationRepository);
            _getMessages = new GetMessagesUseCase(userRepository, messageRepository, notificationRepository);

            _getStations = new GetStationsUseCase(rwRepository);
            _getTrains = new GetTrainsUseCase(rwRepository);
            
            _addToFavorites = new AddToFavoritesUseCase(userRepository, favoritesRepository);
            _removeFromFavorites = new RemoveFromFavoritesUseCase(userRepository, favoritesRepository);
            _getFavorites = new GetFavoritesUseCase(userRepository, favoritesRepository);

            _subscribe = new SubscribeUseCase(userRepository, subscriptionRepository);
            _unSubscribe = new UnSubscribeUseCase(userRepository, subscriptionRepository);
            _getSubscriptions = new GetSubscriptionsUseCase(userRepository, subscriptionRepository);

            _popNotifications = new PopNotificationsUseCase(notificationRepository);

            _ = Task.Run(() => StartAsync());
        }
        public Task StartAsync() => _notificationBackgroundService.StartAsync(_cts.Token);

        public Task StopAsync() => _cts.CancelAsync();

        public void AuthenticateUser(string userId)
        {
            _registerUser.RegisterUserAsync(userId);
        }

        public async Task<List<StationVO>> GetStationAsync(string prefix)
        {
            return await _getStations.GetStationsAsync(prefix);
        }

        public async Task<List<TrainVO>> GetTimesForRouteAsync(RouteVO route)
        {
            return await _getTrains.GetTrainsForRouteAsync(route);
        }

        public async Task AddToFavoritesAsync(string userId, TrainVO train)
        {
            await _addToFavorites.AddToFavoritesAsync(userId, train);
        }

        public async Task RemoveFromFavoritesAsync(string userId, TrainVO train)
        {
            await _removeFromFavorites.RemoveFromFavoritesAsync(userId, train);
        }

        public async Task<List<TrainVO>> GetFavoritesAsync(string userId)
        {
            return await _getFavorites.GetFavoritesAsync(userId);
        }

        public async Task SubscribeAsync(string userId, SubscriptionVO subscription)
        {
            await _subscribe.SubscribeAsync(userId, subscription);
        }

        public async Task UnSubscribeAsync(string userId, SubscriptionVO subscription)
        {
            await _unSubscribe.UnSubscribeAsync(userId, subscription);
        }

        public async Task<List<SubscriptionVO>> GetSubscritionsAsync(string userId)
        {
            return await _getSubscriptions.GetSubscriptionsAsync(userId);
        }
        public async Task<List<NotificationItem>> PopNotifications()
        {
            return await _popNotifications.PopNotifications();
        }

        public async Task<string> GetUserStatusAsync(string userId)
        {
            return await _getUserStatus.GetUserStatusAsync(userId);
        }
        public async Task BanUserAsync(string userId, string targetId)
        {
            await _banUser.BanUserAsync(userId, targetId);
        }

        public async Task UnbanUserAsync(string userId, string targetId)
        {
            await _unbanUser.UnbanUserAsync(userId, targetId);
        }

        public async Task PromoteUserAsync(string userId, string targetId)
        {
            await _promoteUser.PromoteUserAsync(userId, targetId);
        }

        public async Task DemoteUserAsync(string userId, string targetId)
        {
            await _demoteUser.DemoteUserAsync(userId, targetId);
        }

        public async Task SetUsersMaxSubscriptionsAsync(string userId, string targetId, uint maxSubscriptions)
        {
            await _setUsersMaxSubscriptions.SetUsersMaxSubscriptionsAsync(userId, targetId, maxSubscriptions);
        }

        public async Task SetUsersMinIntervalAsync(string userId, string targetId, uint maxSubscriptions)
        {
            await _setUsersMinInterval.SetUsersMinIntervalAsync(userId, targetId, maxSubscriptions);
        }

        public async Task SendFeedbackAsync(string userId, string message)
        {
            await _sendFeedback.SendFeedbackAsync(userId, message);
        }

        public async Task SendMessageAsync(string userId, string targetId, string message)
        {
            await _sendMessage.SendMessageAsync(userId, targetId, message);
        }
        public async Task<List<Message>> GetMessagesAsync(string userId)
        {
            return await _getMessages.GetMessages(userId);
        }
        public async Task<List<UserVO>> GetUsersAsync(string userId, TimeSpan timeSpan)
        {
            return await _getUsers.GetUsersAsync(userId, timeSpan);
        }

    }
}
