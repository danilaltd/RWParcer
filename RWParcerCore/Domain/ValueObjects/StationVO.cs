namespace RWParcerCore.Domain.ValueObjects
{
    public class StationVO : ValueObject
    {
        public string Label { get; private set; }
        internal string Exp { get; private set; }

        public StationVO(string label, string exp)
        {
            Label = label;
            Exp = exp;
        }

        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return Label;
            yield return Exp;
        }
    }
}

