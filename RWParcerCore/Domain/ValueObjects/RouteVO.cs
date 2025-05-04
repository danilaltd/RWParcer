namespace RWParcerCore.Domain.ValueObjects
{
    public class RouteVO(StationVO from, StationVO to) : ValueObject
    {
        public StationVO From { get; private set; } = from;
        public StationVO To { get; private set; } = to;

        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return From;
            yield return To;
        }
    }
}
                            
