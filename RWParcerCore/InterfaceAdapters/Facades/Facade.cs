using Microsoft.EntityFrameworkCore;
using RWParcerCore.Application.Interfaces.IFavoritesService;
using RWParcerCore.Application.Interfaces.IFeedbackService;
using RWParcerCore.Application.Interfaces.IModerator;
using RWParcerCore.Application.Interfaces.INotificationService;
using RWParcerCore.Application.Interfaces.IRWService;
using RWParcerCore.Application.Interfaces.ISubscriptionService;
using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Application.UseCases.FavoritesService;
using RWParcerCore.Application.UseCases.FeedbackService;
using RWParcerCore.Application.UseCases.ModeratorUseCases;
using RWParcerCore.Application.UseCases.NotificationService;
using RWParcerCore.Application.UseCases.RWService;
using RWParcerCore.Application.UseCases.SubscriptionService;
using RWParcerCore.Application.UseCases.UserService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.IServices;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.Infrastructure;
using RWParcerCore.Infrastructure.InMemoryRepositories;
using RWParcerCore.Infrastructure.Repositories;
using RWParcerCore.Infrastructure.Services;
using System.Net;

namespace RWParcerCore.InterfaceAdapters.Facades
{
    public class Facade : IFacade
    {
        private readonly CancellationTokenSource _cts;
        private readonly INotificationBackgroundService _notificationBackgroundService;

        private readonly IRegisterUser _registerUser;
        private readonly IBanUser _banUser;
        private readonly IUnbanUser _unbanUser;
        private readonly IPromoteUser _promoteUser;
        private readonly IDemoteUser _demoteUser;
        private readonly ISetUsersMaxSubscriptions _setUsersMaxSubscriptions;
        private readonly ISetUsersMinInterval _setUsersMinInterval;
        private readonly IGetUsers _getUsers;
        private readonly IGetUserById _getUserById;
        private readonly IIsUserModerator _isUserModerator;
        private readonly IIsUserBanned _isUserBanned;

        private readonly ISendFeedback _sendFeedback;
        private readonly ISendMessage _sendMessage;
        private readonly IGetMessages _getMessages;
        private readonly IGetAllMessages _getAllMessages;

        private readonly IGetStations _getStations;
        private readonly IGetTrains _getTrains;

        private readonly IAddToFavorites _addToFavorites;
        private readonly IIsInFavorites _isInFavorites;
        private readonly IRemoveFromFavorites _removeFromFavorites;
        private readonly IGetFavorites _getFavorites;

        private readonly ISubscribe _subscribe;
        private readonly IUnSubscribe _unSubscribe;
        private readonly IGetSubscriptions _getSubscriptions;

        private readonly IPopNotifications _popNotifications;


        public Facade()
        {
            var proxies = new[]
{
    "127.0.0.1:8090",
    "127.0.0.1:8091",
    "127.0.0.1:8092",
    "127.0.0.1:8093",
    "127.0.0.1:8094",
    //"127.0.0.1:8095",
    //"127.0.0.1:8096",
    //"127.0.0.1:8097",
    //"127.0.0.1:8098",
    //"127.0.0.1:8099",
    //"127.0.0.1:8100",
    //"127.0.0.1:8101",
    //"127.0.0.1:8102",
    //"127.0.0.1:8103",
    //"127.0.0.1:8104",
    //"127.0.0.1:8105",
    //"127.0.0.1:8106",
    //"127.0.0.1:8107",
    //"127.0.0.1:8108",
    //"127.0.0.1:8109"
};




            var factory = new HttpClientFactoryWithProxyRotation(proxies);
            HttpClient httpClient = new();
            httpClient.DefaultRequestHeaders.Add("Cookie", "hg-client-security=2wYWCwYjyj7EbcjAw98T7DTE4GQ; hg-security=jSvnyAzRO13rHxzxDQofaNhudTzZhdMLWREbC5iPNPrQbWMqaYq3EQPi1vGNz_rCZZ5FJBk9B9T1V401kT7hxaNLwppBih0=");
            //IUserRepository userRepository = new InMemoryUserRepository();
            //IFavoritesRepository favoritesRepository = new InMemoryFavoritesRepository();
            //ISubscriptionRepository subscriptionRepository = new InMemorySubscriptionRepository();
            //INotificationRepository notificationRepository = new InMemoryNotificationRepository();
            //IRWRepository rwRepository = new RWParcer(httpClient);
            //IMessageRepository messageRepository = new InMemoryMessageRepository();

            //if (File.Exists("app.db")) File.Delete("app.db");
            //if (File.Exists("app.db-shm")) File.Delete("app.db-shm");
            //if (File.Exists("app.db-wal")) File.Delete("app.db-wal");
            //using (var context = new AppDbContext(options))
            //{
            //    context.Database.EnsureCreated();
            //}
            var options = new DbContextOptionsBuilder<AppDbContext>()
                            .UseNpgsql("Host=db.phzzfofwodzqkppnmjzq.supabase.co;Port=5432;Database=postgres;Username=postgres;Password=mypswhelloworl;SSL Mode=Require;Trust Server Certificate=true")
                            .Options;


            IAppDbContextFactory appDbContextFactory = new AppDbContextFactory(options);

            IUserRepository userRepository = new UserRepository(appDbContextFactory);
            IFavoritesRepository favoritesRepository = new FavoritesRepository(appDbContextFactory);
            ISubscriptionRepository subscriptionRepository = new SubscriptionRepository(appDbContextFactory);
            INotificationRepository notificationRepository = new NotificationRepository(appDbContextFactory);
            IMessageRepository messageRepository = new MessageRepository(appDbContextFactory);
            IRWRepository rwRepository = new RWParcer(factory);

            _notificationBackgroundService = new NotificationBackgroundService(subscriptionRepository, notificationRepository, userRepository, rwRepository, 5, 15); ;
            _cts = new CancellationTokenSource();

            _registerUser = new RegisterUserUseCase(userRepository);
            _banUser = new BanUserUseCase(userRepository);
            _unbanUser = new UnbanUserUseCase(userRepository);
            _promoteUser = new PromoteUserUseCase(userRepository);
            _demoteUser = new DemoteUserUseCase(userRepository);
            _setUsersMaxSubscriptions = new SetUsersMaxSubscriptionsUseCase(userRepository);
            _setUsersMinInterval = new SetUsersMinIntervalUseCase(userRepository);
            _getUsers = new GetUsersUseCase(userRepository);
            _isUserModerator = new IsUserModeratorUseCase(userRepository);
            _isUserBanned = new IsUserBannedUseCase(userRepository);
            _getUserById = new GetUserByIdUseCase(userRepository);

            _sendFeedback = new SendFeedbackUseCase(userRepository, messageRepository, notificationRepository);
            _sendMessage = new SendMessageUseCase(userRepository, messageRepository, notificationRepository);
            _getMessages = new GetMessagesUseCase(userRepository, messageRepository);
            _getAllMessages = new GetAllMessagesUseCase(userRepository, messageRepository);

            _getStations = new GetStationsUseCase(rwRepository, userRepository);
            _getTrains = new GetTrainsUseCase(rwRepository, userRepository);

            _addToFavorites = new AddToFavoritesUseCase(userRepository, favoritesRepository);
            _isInFavorites = new IsInFavoritesUseCase(userRepository, favoritesRepository);
            _removeFromFavorites = new RemoveFromFavoritesUseCase(userRepository, favoritesRepository);
            _getFavorites = new GetFavoritesUseCase(userRepository, favoritesRepository);

            _subscribe = new SubscribeUseCase(userRepository, subscriptionRepository);
            _unSubscribe = new UnSubscribeUseCase(userRepository, subscriptionRepository);
            _getSubscriptions = new GetSubscriptionsUseCase(userRepository, subscriptionRepository);

            _popNotifications = new PopNotificationsUseCase(notificationRepository, userRepository);

            _ = Task.Run(() => StartAsync());
        }
        private Task StartAsync() => _notificationBackgroundService.StartAsync(_cts.Token);

        public Task StopAsync() => _cts.CancelAsync();

        public async Task AuthenticateUser(string userId)
        {
            await _registerUser.RegisterUserAsync(userId);
        }

        public async Task<List<StationVO>> GetStationAsync(string userId, string prefix)
        {
            return await _getStations.GetStationsAsync(userId, prefix);
        }

        public async Task<List<TrainVO>> GetTimesForRouteAsync(string userId, RouteVO route)
        {
            return await _getTrains.GetTrainsForRouteAsync(userId, route);
        }

        public async Task AddToFavoritesAsync(string userId, TrainVO train)
        {
            await _addToFavorites.AddToFavoritesAsync(userId, train);
        }

        public async Task<bool> IsInFavoritesAsync(string userId, TrainVO train)
        {
            return await _isInFavorites.IsInFavoritesAsync(userId, train);
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
        public async Task<List<NotificationVO>> PopNotificationsAsync()
        {
            return await _popNotifications.PopNotifications();
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
        public async Task<List<MessageVO>> GetMessagesAsync(string userId)
        {
            return await _getMessages.GetMessages(userId);
        }

        public async Task<List<MessageVO>> GetAllMessagesAsync(string userId)
        {
            return await _getAllMessages.GetAllMessages(userId);
        }
        public async Task<List<UserVO>> GetUsersAsync(string userId, TimeSpan timeSpan)
        {
            return await _getUsers.GetUsersAsync(userId, timeSpan);
        }

        public async Task<List<SubscriptionVO>> GetSubscritionsAsync(string userId, string targetId)
        {
            return await _getSubscriptions.GetSubscriptionsAsync(userId, targetId);
        }

        public async Task<bool> IsUserModeratorAsync(string userId, string targetId)
        {
            return await _isUserModerator.IsUserModeratorAsync(userId, targetId);
        }

        public async Task<bool> IsUserBannedAsync(string userId, string targetId)
        {
            return await _isUserBanned.IsUserBannedAsync(userId, targetId);
        }

        public async Task<UserVO> GetUserByIdAsync(string userId, string targetId)
        {
            return await _getUserById.GetUserByIdAsync(userId, targetId);
        }
    }

    public class HttpClientFactoryWithProxyRotation
    {
        private readonly List<string> _proxyList;
        private int _currentIndex = 0;
        private readonly object _lock = new();

        public HttpClientFactoryWithProxyRotation(IEnumerable<string> proxyList)
        {
            _proxyList = new List<string>(proxyList);
            if (_proxyList.Count == 0)
                throw new ArgumentException("Proxy list cannot be empty.");
        }

        public HttpClient CreateClient()
        {
            string proxyAddress;
            lock (_lock)
            {
                proxyAddress = _proxyList[_currentIndex];
                _currentIndex = (_currentIndex + 1) % _proxyList.Count;
            }

            var proxy = new WebProxy(proxyAddress);
            var handler = new HttpClientHandler
            {
                Proxy = proxy,
                UseProxy = true
            };

            HttpClient httpClient = new(handler, disposeHandler: true);
            httpClient.DefaultRequestHeaders.Add("Cookie", "hg-client-security=2wYWCwYjyj7EbcjAw98T7DTE4GQ; hg-security=jSvnyAzRO13rHxzxDQofaNhudTzZhdMLWREbC5iPNPrQbWMqaYq3EQPi1vGNz_rCZZ5FJBk9B9T1V401kT7hxaNLwppBih0=");
            return httpClient;
            //return new HttpClient(handler, disposeHandler: true); // важно: disposeHandler
        }
    }

}
