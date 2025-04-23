namespace RWParcerCore.Domain.Entities
{
    internal class User(string id)
    {
        public string Id { get; } = id;
        public bool IsModerator { get; private set; }
        public uint MaxSubscriptions { get; private set; }
        public uint MinSubscriptionsInterval { get; private set; } = 5;
        public bool IsBlocked { get; private set; }

        public void Block()
        {
            IsBlocked = true;
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
            IsModerator = true;
        }

        public void Demote()
        {
            IsModerator = false;
        }

    }

}
