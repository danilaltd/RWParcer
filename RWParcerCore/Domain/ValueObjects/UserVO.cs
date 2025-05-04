namespace RWParcerCore.Domain.ValueObjects
{
    public class UserVO(string id, bool isModerator, uint maxSubscriptions, uint minSubscriptionsInterval, bool isBlocked, DateTime lastActivity) : ValueObject
    {
        public string Id { get; } = id;
        public bool IsModerator { get; private set; } = isModerator;
        public uint MaxSubscriptions { get; private set; } = maxSubscriptions;
        public uint MinUpdateInterval { get; private set; } = minSubscriptionsInterval;
        public bool IsBlocked { get; private set; } = isBlocked;
        public DateTime LastActivity { get; set; } = lastActivity;

        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return Id;
            yield return IsModerator;
            yield return MaxSubscriptions;
            yield return MinUpdateInterval;
            yield return IsBlocked;
            yield return LastActivity;
        }
    }
}
                            
