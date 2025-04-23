using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService.FeedbackService
{
    internal class GetMessagesUseCase(IUserRepository userRepository, IMessageRepository messageRepository, INotificationRepository notificationRepository) : IGetMessages
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IMessageRepository _messageRepository = messageRepository;
        private readonly INotificationRepository _notificationRepository = notificationRepository;

        public async Task<List<Message>> GetMessages(string userId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (await _userRepository.IsUserModeratorAsync(userId))
            {
                return [.. (await _messageRepository.GetAllMessagesAsync())];
            }
            else
            {
                return [.. (await _messageRepository.GetMessagesAsync(userId))];
            }
        }
    }
}
