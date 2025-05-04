namespace RWParcerCore.Application.Interfaces.IFeedbackService
{
    internal interface ISendMessage
    {
        Task SendMessageAsync(string userId, string targetId, string message);
    }
}
