using FluentAssertions;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;
using Xunit;

namespace RWParcerCore.Tests
{
    //set inmemory in facade before tests
    [CollectionDefinition("FacadeTests", DisableParallelization = true)]
    public class FacadeTestsCollection { }

    [Collection("FacadeTests")] // This ensures tests run sequentially within this collection
    public class FacadeTests : IAsyncLifetime
    {
        private readonly string[] _testProxies = [];
        private Facade _facade;
        private readonly CancellationTokenSource _cts = new(TimeSpan.FromSeconds(30)); // 30 second timeout

        public FacadeTests()
        {
            _facade = new Facade(string.Empty, _testProxies);
        }

        public Task InitializeAsync()
        {
            try
            {
                Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] === Starting new test initialization ===");
                _facade = new Facade(string.Empty, _testProxies);
                return Task.CompletedTask;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in InitializeAsync: {ex.Message}");
                throw;
            }
        }

        public async Task DisposeAsync()
        {
            try
            {
                Console.WriteLine($"[{DateTime.Now:HH:mm:ss.fff}] === Cleaning up after test ===");
                if (_facade != null)
                {
                    await _facade.StopAsync();
                }
                _cts.Cancel();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in DisposeAsync: {ex.Message}");
                throw;
            }
        }

        private async Task<T> WithTimeout<T>(Task<T> task, string operationName)
        {
            try
            {
                using var timeoutCts = CancellationTokenSource.CreateLinkedTokenSource(_cts.Token);
                timeoutCts.CancelAfter(TimeSpan.FromSeconds(10));
                
                return await task.WaitAsync(timeoutCts.Token);
            }
            catch (OperationCanceledException)
            {
                Console.WriteLine($"Operation {operationName} timed out");
                throw;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in {operationName}: {ex.Message}");
                throw;
            }
        }

        private async Task WithTimeout(Task task, string operationName)
        {
            try
            {
                using var timeoutCts = CancellationTokenSource.CreateLinkedTokenSource(_cts.Token);
                timeoutCts.CancelAfter(TimeSpan.FromSeconds(10));
                
                await task.WaitAsync(timeoutCts.Token);
            }
            catch (OperationCanceledException)
            {
                Console.WriteLine($"Operation {operationName} timed out");
                throw;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in {operationName}: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task AuthenticateUser_ShouldRegisterNewUser()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: AuthenticateUser_ShouldRegisterNewUser");
            try
            {
                // Arrange
                var userId = "test-user-123";

                // Act
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");

                // Assert
                var user = await WithTimeout<UserVO>(_facade.GetUserByIdAsync(userId, userId), "GetUserById");
                user.Should().NotBeNull();
                user.Id.Should().Be(userId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task GetStationAsync_ShouldReturnStations()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: GetStationAsync_ShouldReturnStations");
            try
            {
                // Arrange
                var userId = "test-user-123";
                var prefix = "Мин";
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");

                // Act
                prefix.Should().NotBeNull();
                var stations = await WithTimeout<List<StationVO>>(_facade.GetStationAsync(userId, prefix), "GetStation");

                // Assert
                stations.Should().NotBeNull();
                stations.Should().BeOfType<List<StationVO>>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task AddToFavorites_ShouldAddTrainToFavorites()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: AddToFavorites_ShouldAddTrainToFavorites");
            try
            {
                // Arrange
                var userId = "test-user-123";
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                
                var train = new TrainVO(
                    trainType: "Скоростной",
                    trainNumber: "123",
                    titleStationFrom: "Минск",
                    titleStationTo: "Гомель",
                    fromStationDb: "Минск",
                    toStationDb: "Гомель",
                    fromTime: DateTimeOffset.Now.ToUnixTimeSeconds(),
                    toTime: DateTimeOffset.Now.AddHours(4).ToUnixTimeSeconds(),
                    trainDays: "1234567",
                    trainDaysExcept: "",
                    fromStationExp: "Минск",
                    toStationExp: "Гомель",
                    durationMinutes: 240
                );

                // Act
                await WithTimeout(_facade.AddToFavoritesAsync(userId, train), "AddToFavorites");

                // Assert
                var isInFavorites = await WithTimeout<bool>(_facade.IsInFavoritesAsync(userId, train), "IsInFavorites");
                isInFavorites.Should().BeTrue();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task Subscribe_ShouldAddSubscription()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: Subscribe_ShouldAddSubscription");
            try
            {
                // Arrange
                var userId = "test-user-123";
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                
                var train = new TrainVO(
                    trainType: "Скоростной",
                    trainNumber: "123",
                    titleStationFrom: "Минск",
                    titleStationTo: "Гомель",
                    fromStationDb: "Минск",
                    toStationDb: "Гомель",
                    fromTime: DateTimeOffset.Now.ToUnixTimeSeconds(),
                    toTime: DateTimeOffset.Now.AddHours(4).ToUnixTimeSeconds(),
                    trainDays: "1234567",
                    trainDaysExcept: "",
                    fromStationExp: "Минск",
                    toStationExp: "Гомель",
                    durationMinutes: 240
                );
                
                var subscription = new SubscriptionVO(train, DateOnly.FromDateTime(DateTime.Now));

                // Act
                await WithTimeout(_facade.SubscribeAsync(userId, subscription), "Subscribe");

                // Assert
                var subscriptions = await WithTimeout<List<SubscriptionVO>>(_facade.GetSubscritionsAsync(userId, userId), "GetSubscriptions");
                subscriptions.Should().NotBeEmpty();
                subscriptions.Should().Contain(s => 
                    s.Train.TrainNumber == train.TrainNumber &&
                    s.Train.TitleStationFrom == train.TitleStationFrom &&
                    s.Train.TitleStationTo == train.TitleStationTo);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task BanUser_ShouldBanTargetUser()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: BanUser_ShouldBanTargetUser");
            try
            {
                // Arrange
                var moderatorId = "moderator-123";
                var targetId = "target-123";

                // Act
                await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateModerator");
                await WithTimeout(_facade.AuthenticateUser(targetId), "AuthenticateTarget");
                await WithTimeout(_facade.BanUserAsync(moderatorId, targetId), "BanUser");

                // Assert
                var isBanned = await WithTimeout<bool>(_facade.IsUserBannedAsync(moderatorId, targetId), "IsUserBanned");
                isBanned.Should().BeTrue();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task SendMessage_ShouldCreateMessage()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: SendMessage_ShouldCreateMessage");
            try
            {
                // Arrange
                var senderId = "moderator-123";
                var receiverId = "receiver-123";
                var message = "Test message";

                // Act
                await WithTimeout(_facade.AuthenticateUser(senderId), "AuthenticateSender");
                await WithTimeout(_facade.AuthenticateUser(receiverId), "AuthenticateReceiver");
                await WithTimeout(_facade.PromoteUserAsync(senderId, senderId), "PromoteUser");
                await WithTimeout(_facade.SendMessageAsync(senderId, receiverId, message), "SendMessage");

                // Assert
                var messages = await WithTimeout<List<MessageVO>>(_facade.GetMessagesAsync(receiverId), "GetMessages");
                messages.Should().NotBeEmpty();
                messages.Should().Contain(m => 
                    m.ReceiverId == receiverId && 
                    m.Content == message);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task UnSubscribe_ShouldRemoveSubscription()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: UnSubscribe_ShouldRemoveSubscription");
            try
            {
                // Arrange
                var userId = "test-user-123";
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                
                var train = new TrainVO(
                    trainType: "Скоростной",
                    trainNumber: "123",
                    titleStationFrom: "Минск",
                    titleStationTo: "Гомель",
                    fromStationDb: "Минск",
                    toStationDb: "Гомель",
                    fromTime: DateTimeOffset.Now.ToUnixTimeSeconds(),
                    toTime: DateTimeOffset.Now.AddHours(4).ToUnixTimeSeconds(),
                    trainDays: "1234567",
                    trainDaysExcept: "",
                    fromStationExp: "Минск",
                    toStationExp: "Гомель",
                    durationMinutes: 240
                );
                
                var subscription = new SubscriptionVO(train, DateOnly.FromDateTime(DateTime.Now));
                await WithTimeout(_facade.SubscribeAsync(userId, subscription), "Subscribe");

                // Act
                await WithTimeout(_facade.UnSubscribeAsync(userId, subscription), "UnSubscribe");

                // Assert
                var subscriptions = await WithTimeout<List<SubscriptionVO>>(_facade.GetSubscritionsAsync(userId, userId), "GetSubscriptions");
                subscriptions.Should().NotContain(s => 
                    s.Train.TrainNumber == train.TrainNumber &&
                    s.Train.TitleStationFrom == train.TitleStationFrom &&
                    s.Train.TitleStationTo == train.TitleStationTo);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task ResetSubscribe_ShouldUpdateSubscription()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: ResetSubscribe_ShouldUpdateSubscription");
            try
            {
                // Arrange
                var userId = "test-user-123";
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                
                var train = new TrainVO(
                    trainType: "Скоростной",
                    trainNumber: "123",
                    titleStationFrom: "Минск",
                    titleStationTo: "Гомель",
                    fromStationDb: "Минск",
                    toStationDb: "Гомель",
                    fromTime: DateTimeOffset.Now.ToUnixTimeSeconds(),
                    toTime: DateTimeOffset.Now.AddHours(4).ToUnixTimeSeconds(),
                    trainDays: "1234567",
                    trainDaysExcept: "",
                    fromStationExp: "Минск",
                    toStationExp: "Гомель",
                    durationMinutes: 240
                );
                
                var oldDate = DateOnly.FromDateTime(DateTime.Now);
                var newDate = oldDate.AddDays(1);
                var subscription = new SubscriptionVO(train, oldDate);
                await WithTimeout(_facade.SubscribeAsync(userId, subscription), "Subscribe");

                // Act
                await WithTimeout(_facade.ResetSubscribeAsync(userId, subscription), "ResetSubscribe");

                // Assert
                var subscriptions = await WithTimeout<List<SubscriptionVO>>(_facade.GetSubscritionsAsync(userId, userId), "GetSubscriptions");
                subscriptions.Should().Contain(s => 
                    s.Train.TrainNumber == train.TrainNumber &&
                    s.Date == oldDate);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task GetFavorites_ShouldReturnAllFavorites()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: GetFavorites_ShouldReturnAllFavorites");
            try
            {
                // Arrange
                var userId = "test-user-123";
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                
                var train1 = new TrainVO(
                    trainType: "Скоростной",
                    trainNumber: "123",
                    titleStationFrom: "Минск",
                    titleStationTo: "Гомель",
                    fromStationDb: "Минск",
                    toStationDb: "Гомель",
                    fromTime: DateTimeOffset.Now.ToUnixTimeSeconds(),
                    toTime: DateTimeOffset.Now.AddHours(4).ToUnixTimeSeconds(),
                    trainDays: "1234567",
                    trainDaysExcept: "",
                    fromStationExp: "Минск",
                    toStationExp: "Гомель",
                    durationMinutes: 240
                );

                var train2 = new TrainVO(
                    trainType: "Пассажирский",
                    trainNumber: "456",
                    titleStationFrom: "Гомель",
                    titleStationTo: "Минск",
                    fromStationDb: "Гомель",
                    toStationDb: "Минск",
                    fromTime: DateTimeOffset.Now.ToUnixTimeSeconds(),
                    toTime: DateTimeOffset.Now.AddHours(5).ToUnixTimeSeconds(),
                    trainDays: "1234567",
                    trainDaysExcept: "",
                    fromStationExp: "Гомель",
                    toStationExp: "Минск",
                    durationMinutes: 300
                );

                await WithTimeout(_facade.AddToFavoritesAsync(userId, train1), "AddToFavorites1");
                await WithTimeout(_facade.AddToFavoritesAsync(userId, train2), "AddToFavorites2");

                // Act
                var favorites = await WithTimeout<List<TrainVO>>(_facade.GetFavoritesAsync(userId), "GetFavorites");

                // Assert
                favorites.Should().HaveCount(2);
                favorites.Should().Contain(t => t.TrainNumber == train1.TrainNumber);
                favorites.Should().Contain(t => t.TrainNumber == train2.TrainNumber);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task RemoveFromFavorites_ShouldRemoveTrainFromFavorites()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: RemoveFromFavorites_ShouldRemoveTrainFromFavorites");
            try
            {
                // Arrange
                var userId = "test-user-123";
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                
                var train = new TrainVO(
                    trainType: "Скоростной",
                    trainNumber: "123",
                    titleStationFrom: "Минск",
                    titleStationTo: "Гомель",
                    fromStationDb: "Минск",
                    toStationDb: "Гомель",
                    fromTime: DateTimeOffset.Now.ToUnixTimeSeconds(),
                    toTime: DateTimeOffset.Now.AddHours(4).ToUnixTimeSeconds(),
                    trainDays: "1234567",
                    trainDaysExcept: "",
                    fromStationExp: "Минск",
                    toStationExp: "Гомель",
                    durationMinutes: 240
                );

                await WithTimeout(_facade.AddToFavoritesAsync(userId, train), "AddToFavorites");

                // Act
                await WithTimeout(_facade.RemoveFromFavoritesAsync(userId, train), "RemoveFromFavorites");

                // Assert
                var isInFavorites = await WithTimeout<bool>(_facade.IsInFavoritesAsync(userId, train), "IsInFavorites");
                isInFavorites.Should().BeFalse();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task GetTimesForRoute_ShouldReturnTrains()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: GetTimesForRoute_ShouldReturnTrains");
            try
            {
                // Arrange
                var userId = "test-user-123";
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                
                var route = new RouteVO(
                    new StationVO("Минск", "Минск"),
                    new StationVO("Гомель", "Гомель")
                );

                // Act
                var trains = await WithTimeout<List<TrainVO>>(_facade.GetTimesForRouteAsync(userId, route), "GetTimesForRoute");

                // Assert
                trains.Should().NotBeNull();
                trains.Should().BeOfType<List<TrainVO>>();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task DemoteUser_ShouldRemoveModeratorStatus()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: DemoteUser_ShouldRemoveModeratorStatus");
            try
            {
                // Arrange
                var moderatorId = "moderator-123";
                var targetId = "target-123";

                // Act
                await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateModerator");
                await WithTimeout(_facade.AuthenticateUser(targetId), "AuthenticateTarget");
                await WithTimeout(_facade.PromoteUserAsync(moderatorId, targetId), "PromoteUser");
                await WithTimeout(_facade.DemoteUserAsync(moderatorId, targetId), "DemoteUser");

                // Assert
                var isModerator = await WithTimeout<bool>(_facade.IsUserModeratorAsync(moderatorId, targetId), "IsUserModerator");
                isModerator.Should().BeFalse();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task SendFeedback_ShouldCreateFeedbackMessage()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: SendFeedback_ShouldCreateFeedbackMessage");
            try
            {
                // Arrange
                var userId = "user-123";
                var message = "Test feedback message";
                var moderatorId = "moderator-123";

                // Act
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateUser");
                await WithTimeout(_facade.SendFeedbackAsync(userId, message), "SendFeedback");

                // Assert
                var messages = await WithTimeout<List<MessageVO>>(_facade.GetAllMessagesAsync(moderatorId), "GetAllMessages");
                messages.Should().Contain(m => 
                    m.Content == message &&
                    m.SenderId == userId);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task GetAllMessages_ShouldReturnAllMessages()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: GetAllMessages_ShouldReturnAllMessages");
            try
            {
                // Arrange
                var userId = "user-123";
                var message1 = "First message";
                var message2 = "Second message";
                var moderatorId = "moderator-123";

                // Act
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateModerator");
                await WithTimeout(_facade.SendFeedbackAsync(userId, message1), "SendFeedback1");
                await WithTimeout(_facade.SendFeedbackAsync(userId, message2), "SendFeedback2");

                // Assert
                var messages = await WithTimeout<List<MessageVO>>(_facade.GetAllMessagesAsync(moderatorId), "GetAllMessages");
                messages.Should().HaveCountGreaterOrEqualTo(2);
                messages.Should().Contain(m => m.Content == message1);
                messages.Should().Contain(m => m.Content == message2);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task PromoteUser_ShouldMakeUserModerator()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: PromoteUser_ShouldMakeUserModerator");
            try
            {
                // Arrange
                var moderatorId = "moderator-123";
                var targetId = "target-123";

                // Act
                await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateModerator");
                await WithTimeout(_facade.AuthenticateUser(targetId), "AuthenticateTarget");
                await WithTimeout(_facade.PromoteUserAsync(moderatorId, targetId), "PromoteUser");

                // Assert
                var isModerator = await WithTimeout<bool>(_facade.IsUserModeratorAsync(moderatorId, targetId), "IsUserModerator");
                isModerator.Should().BeTrue();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task GetMessages_ShouldReturnUserMessages()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: GetMessages_ShouldReturnUserMessages");
            try
            {
                // Arrange
                var userId = "user-123";
                var message = "Test message";
                var moderatorId = "moderator-123";

                // Act
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateModerator");
                await WithTimeout(_facade.PromoteUserAsync(moderatorId, moderatorId), "PromoteUser");
                await WithTimeout(_facade.SendMessageAsync(moderatorId, userId, message), "SendMessage");

                // Assert
                var messages = await WithTimeout<List<MessageVO>>(_facade.GetMessagesAsync(userId), "GetMessages");
                messages.Should().NotBeEmpty();
                messages.Should().Contain(m => m.Content == message);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task GetSubscriptions_ShouldReturnUserSubscriptions()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: GetSubscriptions_ShouldReturnUserSubscriptions");
            try
            {
                // Arrange
                var userId = "test-user-123";
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                
                var train = new TrainVO(
                    trainType: "Скоростной",
                    trainNumber: "123",
                    titleStationFrom: "Минск",
                    titleStationTo: "Гомель",
                    fromStationDb: "Минск",
                    toStationDb: "Гомель",
                    fromTime: DateTimeOffset.Now.ToUnixTimeSeconds(),
                    toTime: DateTimeOffset.Now.AddHours(4).ToUnixTimeSeconds(),
                    trainDays: "1234567",
                    trainDaysExcept: "",
                    fromStationExp: "Минск",
                    toStationExp: "Гомель",
                    durationMinutes: 240
                );
                
                var subscription = new SubscriptionVO(train, DateOnly.FromDateTime(DateTime.Now));
                await WithTimeout(_facade.SubscribeAsync(userId, subscription), "Subscribe");

                // Act
                var subscriptions = await WithTimeout<List<SubscriptionVO>>(_facade.GetSubscritionsAsync(userId, userId), "GetSubscriptions");

                // Assert
                subscriptions.Should().NotBeEmpty();
                subscriptions.Should().Contain(s => 
                    s.Train.TrainNumber == train.TrainNumber &&
                    s.Train.TitleStationFrom == train.TitleStationFrom &&
                    s.Train.TitleStationTo == train.TitleStationTo);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task ValidateRoute_ShouldReturnValidRoute()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: ValidateRoute_ShouldReturnValidRoute");
            try
            {
                // Arrange
                var userId = "test-user-123";
                await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
                
                var route = new RouteVO(
                    new StationVO("Минск", "Минск"),
                    new StationVO("Гомель", "Гомель")
                );

                // Act
                var trains = await WithTimeout<List<TrainVO>>(_facade.GetTimesForRouteAsync(userId, route), "GetTimesForRoute");

                // Assert
                trains.Should().NotBeNull();
                trains.Should().BeOfType<List<TrainVO>>();
                if (trains.Any())
                {
                    trains.Should().AllSatisfy(t => 
                    {
                        t.TitleStationFrom.Should().Be("Минск");
                        t.TitleStationTo.Should().Be("Гомель");
                    });
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task IsUserBanned_ShouldReturnFalseForNonBannedUser()
        {
            Console.WriteLine($"\n[{DateTime.Now:HH:mm:ss.fff}] [TEST] Running: IsUserBanned_ShouldReturnFalseForNonBannedUser");
            try
            {
                // Arrange
                var moderatorId = "moderator-123";
                var targetId = "target-123";

                // Act
                await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateModerator");
                await WithTimeout(_facade.AuthenticateUser(targetId), "AuthenticateTarget");

                // Assert
                var isBanned = await WithTimeout<bool>(_facade.IsUserBannedAsync(moderatorId, targetId), "IsUserBanned");
                isBanned.Should().BeFalse();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Test failed: {ex.Message}");
                throw;
            }
        }

        [Fact]
        public async Task AuthenticateUser_ShouldNotThrowOnReAuth()
        {
            var userId = "re-auth-user";
            await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
            await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUserAgain");
        }

        [Fact]
        public async Task AddAndRemoveFavorite_ShouldWorkConsecutively()
        {
            var userId = "fav-user";
            await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
            var train = new TrainVO("Скоростной", "321", "Минск", "Брест", "Минск", "Брест", DateTimeOffset.Now.ToUnixTimeSeconds(), DateTimeOffset.Now.AddHours(8).ToUnixTimeSeconds(), "1234567", "", "Минск", "Брест", 480);
            await WithTimeout(_facade.AddToFavoritesAsync(userId, train), "AddToFavorites");
            await WithTimeout(_facade.RemoveFromFavoritesAsync(userId, train), "RemoveFromFavorites");
            var isInFavorites = await WithTimeout<bool>(_facade.IsInFavoritesAsync(userId, train), "IsInFavorites");
            isInFavorites.Should().BeFalse();
        }

        [Fact]
        public async Task SubscribeAndUnsubscribe_ShouldWorkConsecutively()
        {
            var userId = "sub-user";
            await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
            var train = new TrainVO("Скоростной", "654", "Минск", "Витебск", "Минск", "Витебск", DateTimeOffset.Now.ToUnixTimeSeconds(), DateTimeOffset.Now.AddHours(2).ToUnixTimeSeconds(), "1234567", "", "Минск", "Витебск", 120);
            var subscription = new SubscriptionVO(train, DateOnly.FromDateTime(DateTime.Now));
            await WithTimeout(_facade.SubscribeAsync(userId, subscription), "Subscribe");
            await WithTimeout(_facade.UnSubscribeAsync(userId, subscription), "UnSubscribe");
            var subscriptions = await WithTimeout<List<SubscriptionVO>>(_facade.GetSubscritionsAsync(userId, userId), "GetSubscriptions");
            subscriptions.Should().NotContain(s => s.Train.TrainNumber == train.TrainNumber);
        }

        [Fact]
        public async Task ResetSubscribe_ShouldNotThrow()
        {
            var userId = "reset-user";
            await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
            var train = new TrainVO("Скоростной", "777", "Минск", "Гродно", "Минск", "Гродно", DateTimeOffset.Now.ToUnixTimeSeconds(), DateTimeOffset.Now.AddHours(1).ToUnixTimeSeconds(), "1234567", "", "Минск", "Гродно", 60);
            var subscription = new SubscriptionVO(train, DateOnly.FromDateTime(DateTime.Now));
            await WithTimeout(_facade.SubscribeAsync(userId, subscription), "Subscribe");
            await WithTimeout(_facade.ResetSubscribeAsync(userId, subscription), "ResetSubscribe");
        }

        [Fact]
        public async Task GetFavorites_ShouldReturnEmptyForNewUser()
        {
            var userId = "empty-fav-user";
            await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
            var favorites = await WithTimeout<List<TrainVO>>(_facade.GetFavoritesAsync(userId), "GetFavorites");
            favorites.Should().BeEmpty();
        }

        [Fact]
        public async Task GetMessages_ShouldReturnEmptyForNewUser()
        {
            var userId = "empty-msg-user";
            await WithTimeout(_facade.AuthenticateUser(userId), "AuthenticateUser");
            var messages = await WithTimeout<List<MessageVO>>(_facade.GetMessagesAsync(userId), "GetMessages");
            messages.Should().BeEmpty();
        }

        [Fact]
        public async Task BanUser_ShouldThrowForNonexistentUser()
        {
            var moderatorId = "moderator-ban";
            var targetId = "nonexistent-user";
            await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateModerator");
            await Assert.ThrowsAsync<KeyNotFoundException>(async () =>
            {
                await WithTimeout(_facade.BanUserAsync(moderatorId, targetId), "BanUser");
            });
        }

        [Fact]
        public async Task DemoteUser_ShouldThrowForNonexistentUser()
        {
            var moderatorId = "moderator-demote";
            var targetId = "nonexistent-user";
            await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateModerator");
            await Assert.ThrowsAsync<KeyNotFoundException>(async () =>
            {
                await WithTimeout(_facade.DemoteUserAsync(moderatorId, targetId), "DemoteUser");
            });
        }

        [Fact]
        public async Task SendMessageToSelf_ShouldWork()
        {
            var moderatorId = "self-msg-moderator";
            var message = "Hello, myself!";
            await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateUser");
            await WithTimeout(_facade.SendMessageAsync(moderatorId, moderatorId, message), "SendMessage");
            var messages = await WithTimeout<List<MessageVO>>(_facade.GetMessagesAsync(moderatorId), "GetMessages");
            messages.Should().Contain(m => m.Content == message);
        }

        [Fact]
        public async Task SetUsersMaxSubscriptionsAsync_ShouldNotThrow()
        {
            var moderatorId = "moderator-maxsub";
            var targetId = "target-maxsub";
            await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateModerator");
            await WithTimeout(_facade.AuthenticateUser(targetId), "AuthenticateTarget");
            await WithTimeout(_facade.SetUsersMaxSubscriptionsAsync(moderatorId, targetId, 5), "SetUsersMaxSubscriptions");
        }

        [Fact]
        public async Task SetUsersMinIntervalAsync_ShouldNotThrow()
        {
            var moderatorId = "moderator-minint";
            var targetId = "target-minint";
            await WithTimeout(_facade.AuthenticateUser(moderatorId), "AuthenticateModerator");
            await WithTimeout(_facade.AuthenticateUser(targetId), "AuthenticateTarget");
            await WithTimeout(_facade.SetUsersMinIntervalAsync(moderatorId, targetId, 1), "SetUsersMinInterval");
        }
    }
} 