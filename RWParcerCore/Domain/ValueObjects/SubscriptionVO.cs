namespace RWParcerCore.Domain.ValueObjects
{
    public class SubscriptionVO : ValueObject
    {
        public TrainVO Train { get; private set; }
        public DateOnly Date { get; private set; }

        public SubscriptionVO(
            TrainVO train,
            DateOnly date
        )
        {
            Train = train;
            Date = date;
        }

        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return Train;
            yield return Date;
        }
    }
}

