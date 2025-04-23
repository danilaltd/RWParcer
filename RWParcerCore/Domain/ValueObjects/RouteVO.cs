
namespace RWParcerCore.Domain.ValueObjects
{
    public class RouteVO : ValueObject
    {
        public StationVO From { get; private set; }
        public StationVO To { get; private set; }

        public RouteVO(StationVO from, StationVO to)
        {
            From = from;
            To = to;
        }

        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return From;
            yield return To;
        }
    }
}
                            
