namespace RWParcerCore.Application.Interfaces.IUserService.IFeedbackService
{
    internal interface ISendFeedback
    {
        Task SendFeedbackAsync(string userId, string message);
    }
}
