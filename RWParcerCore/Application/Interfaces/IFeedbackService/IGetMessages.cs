using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IFeedbackService
{
    internal interface IGetMessages
    {
        Task<List<MessageVO>> GetMessages(string userId);
    }
}
