namespace RWParcerCore.Domain.ValueObjects
{
    public class SubscriptionVO(
        TrainVO train,
        DateOnly date
        ) : ValueObject
    {
        public TrainVO Train { get; private set; } = train;
        public DateOnly Date { get; private set; } = date;

        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return Train;
            yield return Date;
        }
    }
}

