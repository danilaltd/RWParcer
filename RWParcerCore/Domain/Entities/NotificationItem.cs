namespace RWParcerCore.Domain.Entities
{
    public class NotificationItem(string id, string msg)
    {
        public Guid Id { get; private set; } = Guid.NewGuid();
        public string UserId { get; private set; } = id;
        public string Message { get; private set; } = msg;
    }
}
