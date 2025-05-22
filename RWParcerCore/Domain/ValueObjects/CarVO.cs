namespace RWParcerCore.Domain.ValueObjects
{
    internal class CarVO(CarType type, uint number, List<uint> freeSeats) : ValueObject
    {
        public CarType Type { get; private set; } = type;
        public uint Number { get; private set; } = number;
        public List<uint> FreeSeats { get; private set; } = freeSeats;
        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return Type;
            yield return Number;
            foreach (var item in FreeSeats.OrderBy(x => x))
            {
                yield return item;
            }
        }
    }


}
