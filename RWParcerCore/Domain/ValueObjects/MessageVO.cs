namespace RWParcerCore.Domain.ValueObjects
{
    public class MessageVO(string senderId, string receiverId, string content, DateTime sentDate) : ValueObject
    {
        public string SenderId { get; set; } = senderId;
        public string ReceiverId { get; set; } = receiverId;
        public string Content { get; set; } = content;
        public DateTime SentDate { get; set; } = sentDate;
        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return SenderId;
            yield return ReceiverId;
            yield return Content;
            yield return SentDate;
        }
    }
}
                            
