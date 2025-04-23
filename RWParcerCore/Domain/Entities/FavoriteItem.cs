using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.Entities
{
    internal class FavoriteItem(string id, TrainVO train)
    {
        public Guid Id { get; private set; } = Guid.NewGuid();
        public string UserId { get; private set; } = id;
        public TrainVO Train { get; private set; } = train;
    }
}
