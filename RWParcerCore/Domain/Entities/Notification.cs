namespace RWParcerCore.Domain.Entities
{
    internal class Notification(string id, string content)
    {
        public Guid Id { get; private set; } = Guid.NewGuid();
        public string UserId { get; private set; } = id;
        public string Content { get; private set; } = content;
    }
}
