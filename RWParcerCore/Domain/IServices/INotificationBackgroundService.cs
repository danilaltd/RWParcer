namespace RWParcerCore.Domain.IServices
{
    internal interface INotificationBackgroundService
    {
        Task StartAsync(CancellationToken cancellationToken);
    }

}
