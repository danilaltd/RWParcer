using RWParcerCore.Application.Interfaces.IFeedbackService;
using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.FeedbackService
{
    internal class SendFeedbackUseCase(IUserRepository userRepository, IMessageRepository messageRepository, INotificationRepository notificationRepository) : ISendFeedback
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IMessageRepository _messageRepository = messageRepository;
        private readonly INotificationRepository _notificationRepository = notificationRepository;

        public async Task SendFeedbackAsync(string userId, string message)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");

            await _messageRepository.AddAsync(new(Guid.NewGuid(), userId, "moderator", message));
            foreach (var user in await _userRepository.GetAllModerators())
            {
                await _notificationRepository.AddAsync(new(Guid.NewGuid(), user.Id, $"Новое сообщение от {userId}:\n{message}"));
            }
        }
    }
}
