namespace RWParcerCore.Domain.ValueObjects
{
    public class StationVO(string label, string exp) : ValueObject
    {
        public string Label { get; private set; } = label;
        internal string Exp { get; private set; } = exp;

        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return Label;
            yield return Exp;
        }
    }
}

