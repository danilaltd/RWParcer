namespace RWParcerCore.Domain.Entities
{
    internal class User
    {
        public string Id { get; private set; }
        public bool IsModerator { get; private set; }
        public uint MaxSubscriptions { get; private set; } = 5;
        public uint MinSubscriptionsInterval { get; private set; } = 15;
        public bool IsBlocked { get; private set; }
        public DateTime LastActivity { get; set; } = DateTime.UtcNow;

        public User(string id)
        {
            Id = id;
        }

        private User(){}

        public void Block()
        {
            IsBlocked = true;
            IsModerator = false;
        }

        public void Unblock()
        {
            IsBlocked = false;
        }

        public void ChangeSubscriptionsLimits(uint maxSubscriptions)
        {
            MaxSubscriptions = maxSubscriptions;
        }

        public void ChangeIntervalLimits(uint interval)
        {
            MinSubscriptionsInterval = interval;
        }
        public void Promote()
        {
            IsBlocked = false;
            IsModerator = true;
        }

        public void Demote()
        {
            IsModerator = false;
        }

    }

}
