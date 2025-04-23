using Newtonsoft.Json;

namespace RWParcerCore.Domain.DTOs
{
    internal class RepoStation
    {
        [JsonProperty("prefix")]
        public string? Prefix { get; set; }

        [JsonProperty("label")]
        public string? Label { get; set; }

        [JsonProperty("label_tail")]
        public string? LabelTail { get; set; }

        [JsonProperty("value")]
        public string? Value { get; set; }

        [JsonProperty("gid")]
        public string? Gid { get; set; }

        [JsonProperty("lon")]
        public double Lon { get; set; }

        [JsonProperty("lat")]
        public double Lat { get; set; }

        [JsonProperty("exp")]
        public string? Exp { get; set; }

        [JsonProperty("ecp")]
        public string? Ecp { get; set; }

        [JsonProperty("otd")]
        public string? Otd { get; set; }
    }
}
