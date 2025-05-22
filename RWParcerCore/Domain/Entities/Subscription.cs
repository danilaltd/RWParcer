using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.Entities
{
    internal class Subscription
    {
        public Guid Id { get; private set; }
        public string UserId { get; private set; }
        public SubscriptionVO Details { get; private set; }
        public DateTime? LastUpdate { get; set; }
        public List<CarVO> LastState { get; set; } = [];

        private Subscription() 
        { 
            UserId = null!;
            Details = null!;
        }
        public Subscription(Guid id, string userId, SubscriptionVO details)
        {
            Id = id;
            UserId = userId;
            Details = details;
        }
    }
}
