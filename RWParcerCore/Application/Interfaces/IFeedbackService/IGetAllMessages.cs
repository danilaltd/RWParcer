using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Application.Interfaces.IFeedbackService
{
    internal interface IGetAllMessages
    {
        Task<List<MessageVO>> GetAllMessages(string userId);
    }
}
