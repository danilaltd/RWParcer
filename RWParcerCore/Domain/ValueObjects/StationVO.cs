namespace RWParcerCore.Domain.ValueObjects
{
    public class StationVO(string label, string value, string exp) : ValueObject
    {
        public string Label { get; private set; } = label;
        public string Value { get; private set; } = value;
        internal string Exp { get; private set; } = exp;

        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return Label;
            yield return Value;
            yield return Exp;
        }
    }
}
                            
