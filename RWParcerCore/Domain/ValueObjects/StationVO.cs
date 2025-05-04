using System.Text.Json.Serialization;

namespace RWParcerCore.Domain.ValueObjects
{
    public class StationVO : ValueObject
    {
        public string Label { get; private set; }
        public string Value { get; private set; }
        internal string Exp { get; private set; }

        public StationVO(string label, string value, string exp)
        {
            Label = label;
            Value = value;
            Exp = exp;
        }

        protected override IEnumerable<object> GetEqualityComponents()
        {
            yield return Label;
            yield return Value;
            yield return Exp;
        }
    }
}
                            
