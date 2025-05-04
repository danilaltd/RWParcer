using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using System.Reflection;
using System.Runtime.Serialization;

namespace RWParcer
{
    public class PrivateFieldsAndBypassCtorResolver : DefaultContractResolver
    {
        public PrivateFieldsAndBypassCtorResolver()
        {
            this.IgnoreSerializableInterface = true;
            this.IgnoreSerializableAttribute = true;
        }

        protected override IList<JsonProperty> CreateProperties(Type type, MemberSerialization memberSerialization)
        {
            var fields = type
                .GetFields(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                .Select(f => base.CreateProperty(f, memberSerialization));

            var props = type
                .GetProperties(BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                .Select(p => base.CreateProperty(p, memberSerialization));

            var all = fields.Concat(props).ToList();

            foreach (var jp in all)
            {
                jp.Writable = true;
                jp.Readable = true;
            }

            return all;
        }

        protected override JsonObjectContract CreateObjectContract(Type objectType)
        {
            var contract = base.CreateObjectContract(objectType);

            contract.DefaultCreator = () => FormatterServices.GetUninitializedObject(objectType);
            contract.DefaultCreatorNonPublic = true;

            return contract;
        }
    }

}