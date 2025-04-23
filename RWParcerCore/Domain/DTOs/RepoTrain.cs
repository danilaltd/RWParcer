using Newtonsoft.Json;

namespace RWParcerCore.Domain.DTOs
{
    internal class RepoTrain
    {
        [JsonProperty("index")]
        public int? Index { get; set; }

        [JsonProperty("is_main_from")]
        public string? IsMainFrom { get; set; }

        [JsonProperty("is_main_to")]
        public string? IsMainTo { get; set; }

        [JsonProperty("train_type")]
        public string? TrainType { get; set; }

        [JsonProperty("car_accessory")]
        public string? CarAccessory { get; set; }

        [JsonProperty("train_number")]
        public string? TrainNumber { get; set; }

        [JsonProperty("train_thread")]
        public string? TrainThread { get; set; }

        [JsonProperty("title")]
        public string? Title { get; set; }

        [JsonProperty("title_station_from")]
        public string? TitleStationFrom { get; set; }

        [JsonProperty("title_station_to")]
        public string? TitleStationTo { get; set; }

        [JsonProperty("from_station")]
        public string? FromStation { get; set; }

        [JsonProperty("from_station_exp")]
        public string? FromStationExp { get; set; }

        [JsonProperty("from_station_db")]
        public string? FromStationDb { get; set; }

        [JsonProperty("from_time")]
        public long? FromTime { get; set; }

        [JsonProperty("from_time_local")]
        public long? FromTimeLocal { get; set; }

        [JsonProperty("to_station")]
        public string? ToStation { get; set; }

        [JsonProperty("to_station_exp")]
        public string? ToStationExp { get; set; }

        [JsonProperty("to_station_db")]
        public string? ToStationDb { get; set; }

        [JsonProperty("to_time")]
        public long? ToTime { get; set; }

        [JsonProperty("to_time_local")]
        public long? ToTimeLocal { get; set; }

        [JsonProperty("duration")]
        public string? Duration { get; set; }

        [JsonProperty("duration_minutes")]
        public int? DurationMinutes { get; set; }

        [JsonProperty("car_category")]
        public string? CarCategory { get; set; }

        [JsonProperty("places")]
        public List<Place>? Places { get; set; }

        [JsonProperty("prices_by_direction")]
        public List<object>? PricesByDirection { get; set; }

        [JsonProperty("min_price")]
        public decimal? MinPrice { get; set; }

        [JsonProperty("train_days")]
        public string? TrainDays { get; set; }

        [JsonProperty("train_days_except")]
        public string? TrainDaysExcept { get; set; }

        [JsonProperty("train_stops")]
        public string? TrainStops { get; set; }

        [JsonProperty("is_left")]
        public bool? IsLeft { get; set; }

        [JsonProperty("from_date_part")]
        public string? FromDatePart { get; set; }

        [JsonProperty("to_date_part")]
        public string? ToDatePart { get; set; }

        [JsonProperty("service")]
        public string? Service { get; set; }

        [JsonProperty("info")]
        public List<object>? Info { get; set; }

        [JsonProperty("all_stations")]
        public List<string>? AllStations { get; set; }

        [JsonProperty("route_tariffs")]
        public List<object>? RouteTariffs { get; set; }

        [JsonProperty("ticket_selling_allowed")]
        public bool? TicketSellingAllowed { get; set; }

        [JsonProperty("is_special_train")]
        public bool? IsSpecialTrain { get; set; }

        [JsonProperty("is_bike_allowed")]
        public bool? IsBikeAllowed { get; set; }

        [JsonProperty("days_of_sale")]
        public int? DaysOfSale { get; set; }

        [JsonProperty("is_ereg_possible")]
        public bool? IsEregPossible { get; set; }

        [JsonProperty("is_class_train")]
        public bool? IsClassTrain { get; set; }

        [JsonProperty("is_fast_train")]
        public bool? IsFastTrain { get; set; }

        [JsonProperty("ticket_selling_allowed_ex")]
        public TicketSellingAllowedEx? TicketSellingAllowedEx { get; set; }

        [JsonProperty("is_by")]
        public bool? IsBy { get; set; }

        [JsonProperty("from_time_formatted")]
        public string? FromTimeFormatted { get; set; }

        [JsonProperty("from_time_formatted_local")]
        public string? FromTimeFormattedLocal { get; set; }

        [JsonProperty("to_time_formatted")]
        public string? ToTimeFormatted { get; set; }

        [JsonProperty("to_time_formatted_local")]
        public string? ToTimeFormattedLocal { get; set; }
    }

    public class Place
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

    public class TicketSellingAllowedEx
    {
        [JsonProperty("status")]
        public bool? Status { get; set; }
    }


}
