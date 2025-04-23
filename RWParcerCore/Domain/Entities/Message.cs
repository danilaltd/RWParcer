namespace RWParcerCore.Domain.Entities
{
    internal class Message(string senderId, string receiverId, string text)
    {
        public Guid Id { get; } = Guid.NewGuid();
        public string SenderId { get; set; } = senderId;
        public string ReceiverId { get; set; } = receiverId;
        public string Content { get; set; } = text;
        public DateTime SentDate { get; set; } = DateTime.Now;
        public List<string> ReadBy { get; private set; } = [];

        public void MarkAsRead(string userId)
        {
            ReadBy.Add(userId);
        }
    }

}
