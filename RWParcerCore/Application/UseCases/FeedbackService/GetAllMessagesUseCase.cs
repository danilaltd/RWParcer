using RWParcerCore.Application.Interfaces.IFeedbackService;
using RWParcerCore.Domain.IRepositories;
using RWParcerCore.Domain.Mappers;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.UseCases.FeedbackService
{
    internal class GetAllMessagesUseCase(IUserRepository userRepository, IMessageRepository messageRepository) : IGetAllMessages
    {
        private readonly IUserRepository _userRepository = userRepository;
        private readonly IMessageRepository _messageRepository = messageRepository;

        public async Task<List<MessageVO>> GetAllMessages(string userId)
        {
            if (!await _userRepository.IsUserRegistredAsync(userId)) throw new KeyNotFoundException($"User with ID {userId} not found");
            await _userRepository.UpdateActivityAsync(userId);
            if (await _userRepository.IsUserBannedAsync(userId)) throw new UnauthorizedAccessException($"User {userId} is banned");
            if (!await _userRepository.IsUserModeratorAsync(userId)) throw new UnauthorizedAccessException($"Only moderators can view all messages {userId}");
            return [.. (await _messageRepository.GetAllMessagesAsync()).Select(item => MessageMapper.FromEntity(item))];
        }
    }
}
