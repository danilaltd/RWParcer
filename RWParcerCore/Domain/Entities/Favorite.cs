using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.Entities
{
    internal class Favorite
    {
        public Favorite(Guid id, string userId, TrainVO train)
        {
            Id = id;
            UserId = userId;
            TrainInfo = train;
        }

        private Favorite() { }
        public Guid Id { get; private set; }
        public string UserId { get; private set; }
        public TrainVO TrainInfo { get; private set; }
    }
}
