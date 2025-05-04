using Newtonsoft.Json;

namespace RWParcerCore.Domain.DTOs
{
    internal class TicketSellingAllowedEx
    {
        [JsonProperty("status")]
        public bool? Status { get; set; }
    }


}
