using RWParcerCore.Domain.ValueObjects;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RWParcerCore.Infrastructure.Converters
{
    internal class RouteVOConverter : JsonConverter<RouteVO>
    {
        public override RouteVO Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            using var jsonDoc = JsonDocument.ParseValue(ref reader);
            var root = jsonDoc.RootElement;

            // Extract from station
            if (!root.TryGetProperty("from", out var fromElement))
                throw new JsonException("Property 'from' not found.");
            var fromOptions = new JsonSerializerOptions(options)
            {
                Converters = { new StationVOConverter() }
            };
            StationVO from = JsonSerializer.Deserialize<StationVO>(fromElement.GetRawText(), fromOptions)
                ?? throw new JsonException("Failed to deserialize from StationVO.");

            // Extract to station
            if (!root.TryGetProperty("to", out var toElement))
                throw new JsonException("Property 'to' not found.");
            var toOptions = new JsonSerializerOptions(options)
            {
                Converters = { new StationVOConverter() }
            };
            StationVO to = JsonSerializer.Deserialize<StationVO>(toElement.GetRawText(), toOptions)
                ?? throw new JsonException("Failed to deserialize to StationVO.");

            return new RouteVO(from, to);
        }

        public override void Write(Utf8JsonWriter writer, RouteVO value, JsonSerializerOptions options)
        {
            writer.WriteStartObject();

            writer.WritePropertyName("from");
            var fromOptions = new JsonSerializerOptions(options)
            {
                Converters = { new StationVOConverter() }
            };
            JsonSerializer.Serialize(writer, value.From, fromOptions);

            writer.WritePropertyName("to");
            var toOptions = new JsonSerializerOptions(options)
            {
                Converters = { new StationVOConverter() }
            };
            JsonSerializer.Serialize(writer, value.To, toOptions);

            writer.WriteEndObject();
        }
    }
} 