using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.Entities
{
    internal class Subscription
    {
        public Guid Id { get; private set; }
        public string UserId { get; private set; }
        public SubscriptionVO Details { get; private set; }
        public DateTime? LastUpdate { get; set; }
        //public TicketFilterVO Filter { get; private set; } = new();
        public uint Interval { get; private set; }
        public Dictionary<int, List<int>>? LastState { get; set; }

        private Subscription() { }
        public Subscription(Guid id, string userId, SubscriptionVO details, uint interval)
        {
            Id = id;
            UserId = userId;
            Details = details;
            Interval = interval;
        }
    }
}
