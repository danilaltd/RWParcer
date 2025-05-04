using RWParcerCore.Application.Interfaces.IFeedbackService;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.FeedbackService
{
    internal class SendMessageUseCase(IUserRepository userRepository, IMessageRepository messageRepository, INotificationRepository notificationRepository) : ISendMessage
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IMessageRepository _messageRepository = messageRepository;
        private readonly INotificationRepository _notificationRepository = notificationRepository;

        public async Task SendMessageAsync(string userId, string targetUserId , string message)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (!await _userRepository.IsUserRegistredAsync(targetUserId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (!await _userRepository.IsUserModeratorAsync(userId)) throw new UnauthorizedAccessException($"Only moderators can send messages {userId}");

            await _messageRepository.AddAsync(new(Guid.NewGuid(), userId, targetUserId, message));
            await _notificationRepository.AddAsync(new(Guid.NewGuid(), targetUserId, message));
            
        }
    }
}
