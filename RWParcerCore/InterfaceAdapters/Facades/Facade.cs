using RWParcerCore.Application.Interfaces.INotificationService;
using RWParcerCore.Application.Interfaces.IRWService;
using RWParcerCore.Application.Interfaces.IUserService;
using RWParcerCore.Application.Interfaces.IUserService.IFavoritesService;
using RWParcerCore.Application.Interfaces.IUserService.ISubscriptionService;
using RWParcerCore.Application.UseCases.NotificationService;
using RWParcerCore.Application.UseCases.RWService;
using RWParcerCore.Application.UseCases.UserService;
using RWParcerCore.Application.UseCases.UserService.FavoritesService;
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
        private CancellationTokenSource _cts;
        private readonly INotificationBackgroundService _notificationBackgroundService;

        private readonly IRegisterUser _registerUser;
        private readonly IGetStations _getStations;
        private readonly IGetTrains _getTrains;

        private readonly IAddToFavorites _addToFavorites;
        private readonly IRemoveFromFavorites _removeFromFavorites;
        private readonly IGetFavorites _getFavorites;

        private readonly ISubscribe _subscribe;
        private readonly IUnSubscribe _unSubscribe;
        private readonly IGetSubscriptions _getSubscriptions;

        private readonly IPopNotifications _popNotifications;

        private Facade()
        {
            HttpClient httpClient = new();
            
            IUserRepository userRepository = new InMemoryUserRepository();
            IFavoritesRepository favoritesRepository = new InMemoryFavoritesRepository();
            ISubscriptionRepository subscriptionRepository = new InMemorySubscriptionRepository();
            INotificationRepository notificationRepository = new InMemoryNotificationRepository(); 
            IRWRepository rwRepository = new RWParcer(httpClient);
            
            _notificationBackgroundService = new NotificationBackgroundService(subscriptionRepository, notificationRepository, rwRepository, httpClient, 5, 15); ;
            _cts = new CancellationTokenSource();

            _registerUser = new RegisterUserUseCase(userRepository);
            _getStations = new GetStationsUseCase(rwRepository);
            _getTrains = new GetTrainsUseCase(rwRepository);
            
            _addToFavorites = new AddToFavoritesUseCase(userRepository, favoritesRepository);
            _removeFromFavorites = new RemoveFromFavoritesUseCase(userRepository, favoritesRepository);
            _getFavorites = new GetFavoritesUseCase(userRepository, favoritesRepository);

            _subscribe = new SubscribeUseCase(userRepository, subscriptionRepository);
            _unSubscribe = new UnSubscribeUseCase(userRepository, subscriptionRepository);
            _getSubscriptions = new GetSubscriptionsUseCase(userRepository, subscriptionRepository);

            _popNotifications = new PopNotificationsUseCase(notificationRepository);
        }

        public async static Task<Facade> CreateAsync()
        {
            Facade facade = new Facade();
            _ = Task.Run(() => facade.StartAsync());
            return facade;
        }

        public Task StartAsync() => _notificationBackgroundService.StartAsync(_cts.Token);

        public Task StopAsync() => _cts.CancelAsync();

        public void AuthenticateUser(string userId)
        {
            _registerUser.RegisterUser(userId);
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






        //public void SendFeedback(Message message)
        //{
        //    _feedbackService.SendFeedback(message);
        //}

        // Можно добавить и другие методы, объединяющие функциональность сервисов
    }

}
