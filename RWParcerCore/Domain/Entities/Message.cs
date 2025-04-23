namespace RWParcerCore.Domain.Entities
{
    internal class Message
    {
        public Guid Id { get; } = Guid.NewGuid();
        public User Sender { get; set; }
        public User Receiver { get; set; }
        public string Text { get; set; }
        public DateTime SentDate { get; set; }
        public bool IsRead { get; private set; }

        public Message(User sender, User receiver, string text)
        {
            Sender = sender;
            Receiver = receiver;
            Text = text;
        }

        public void MarkAsRead()
        {
            IsRead = true;
        }
    }

}
