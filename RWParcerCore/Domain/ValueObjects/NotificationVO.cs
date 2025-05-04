namespace RWParcerCore.Domain.ValueObjects
{
    public class NotificationVO(string userId, string content) : ValueObject
    {
        public string UserId { get; private set; } = userId;
        public string Content { get; private set; } = content;
        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return UserId;
            yield return Content;
        }
    }
}
                            
