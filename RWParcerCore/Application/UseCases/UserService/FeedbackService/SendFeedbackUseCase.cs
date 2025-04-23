using RWParcerCore.Domain.IRepositories;

namespace RWParcerCore.Application.UseCases.UserService.FeedbackService
{
    internal class SendFeedbackUseCase(IUserRepository userRepository, IMessageRepository messageRepository) : ISendFeedback
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IMessageRepository _messageRepository = messageRepository;

        public async Task SendFeedbackAsync(string userId, string message)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");

            await _messageRepository.AddMessageAsync(new(userId, "moderator", message));
        }
    }
}
