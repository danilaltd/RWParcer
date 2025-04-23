namespace RWParcerCore.Application.UseCases.UserService.FeedbackService
{
    internal interface ISendFeedback
    {
        Task SendFeedbackAsync(string userId, string message);
    }
}
