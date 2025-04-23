namespace RWParcerCore.Application.Interfaces.IUserService.IFeedbackService
{
    internal interface ISendMessage
    {
        Task SendMessageAsync(string userId, string targetId, string message);
    }
}
