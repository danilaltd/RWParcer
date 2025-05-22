namespace RWParcerCore.Domain.Entities
{
    internal class Message
    {
        public Guid Id { get; private set; }
        public string SenderId { get; set; }
        public string ReceiverId { get; set; }
        public string Content { get; set; }
        public DateTime SentDate { get; set; } = DateTime.UtcNow;
        public List<string> ReadBy { get; private set; } = [];

        private Message() 
        { 
            SenderId = null!;
            ReceiverId = null!;
            Content = null!;
        }
        public Message(Guid id, string senderId, string receiverId, string content)
        {
            Id = id;
            SenderId = senderId;
            ReceiverId = receiverId;
            Content = content;
        }

        public void MarkAsRead(string userId)
        {
            ReadBy.Add(userId);
        }
    }

}
