namespace RWParcerCore.Application.UseCases.UserService.FeedbackService
{
    internal interface ISendMessage
    {
        Task SendMessageAsync(string userId, string targetId, string message);
    }
}
