using Newtonsoft.Json;

namespace RWParcerCore.Domain.DTOs
{
    internal class Place
    {
        [JsonProperty("car_type")]
        public int? CarType { get; set; }
        
        [JsonProperty("free_seats")]
        public string? FreeSeats { get; set; }
        
        [JsonProperty("price")]
        public decimal? Price { get; set; }
        
        [JsonProperty("available")]
        public bool? Available { get; set; }
        
        [JsonProperty("price_type")]
        public string? PriceType { get; set; }
        
        [JsonProperty("price_type_spepd")]
        public string? PriceTypeSpepd { get; set; }
    }


}
