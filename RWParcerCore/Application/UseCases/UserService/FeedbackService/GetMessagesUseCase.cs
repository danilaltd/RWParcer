using RWParcerCore.Application.Interfaces.IUserService.IFeedbackService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.Mappers;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.UserService.FeedbackService
{
    internal class GetMessagesUseCase(IUserRepository userRepository, IMessageRepository messageRepository, INotificationRepository notificationRepository) : IGetMessages
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IMessageRepository _messageRepository = messageRepository;
        private readonly INotificationRepository _notificationRepository = notificationRepository;

        public async Task<List<MessageVO>> GetMessages(string userId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (await _userRepository.IsUserModeratorAsync(userId))
            {
                return [.. (await _messageRepository.GetAllMessagesAsync()).Select(item => MessageMapper.FromEntity(item))];
            }
            else
            {
                return [.. (await _messageRepository.GetUserMessagesAsync(userId)).Select(item => MessageMapper.FromEntity(item))];
            }
        }
    }
}
