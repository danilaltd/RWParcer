namespace RWParcerCore.Domain.Entities
{
    internal class Notification(Guid id, string userId, string content)
    {
        public Guid Id { get; private set; } = id;
        public string UserId { get; private set; } = userId;
        public string Content { get; private set; } = content;
    }
}
