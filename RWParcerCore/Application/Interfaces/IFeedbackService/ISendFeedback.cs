namespace RWParcerCore.Application.Interfaces.IFeedbackService
{
    internal interface ISendFeedback
    {
        Task SendFeedbackAsync(string userId, string message);
    }
}
