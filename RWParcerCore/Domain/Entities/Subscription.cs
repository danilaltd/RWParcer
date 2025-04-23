using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.Entities
{
    internal class Subscription(string id, SubscriptionVO subscription, uint interval)
    {
        public Guid Id { get; private set; } = Guid.NewGuid();
        public string UserId { get; private set; } = id;
        public SubscriptionVO Details { get; private set; } = subscription;
        public DateTime? LastUpdate { get; set; }
        //public TicketFilterVO Filter { get; private set; } = new();
        public uint Interval { get; private set; } = interval;
        public Dictionary<int, List<int>>? LastState { get; set; }
    }
}
