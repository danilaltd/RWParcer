using RWParcerCore.Domain.Entities;

namespace RWParcerCore.Application.UseCases.UserService.FeedbackService
{
    internal interface IGetMessages
    {
        Task<List<Message>> GetMessages(string userId);
    }
}
