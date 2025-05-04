using RWParcerCore.Domain.ValueObjects;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RWParcerCore.Infrastructure.Converters
{
    internal class SubscriptionVOConverter : JsonConverter<SubscriptionVO>
    {
        public override SubscriptionVO Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            using var jsonDoc = JsonDocument.ParseValue(ref reader);
            var root = jsonDoc.RootElement;

            if (!root.TryGetProperty("date", out var dateElement))
            {
                throw new JsonException("Property 'date' not found in JSON.");
            }
            string dateStr = dateElement.GetString()!;
            if (!DateOnly.TryParse(dateStr, out DateOnly date))
            {
                throw new JsonException($"Invalid date format: {dateStr}");
            }

            if (!root.TryGetProperty("train", out var trainJson))
            {
                throw new JsonException("Property 'train' not found in JSON.");
            }
            var trainOptions = new JsonSerializerOptions(options)
            {
                Converters = { new TrainVOConverter() }
            };
            TrainVO train = JsonSerializer.Deserialize<TrainVO>(trainJson.GetRawText(), trainOptions)
                ?? throw new JsonException("Failed to deserialize TrainVO.");

            return new SubscriptionVO(train, date);
        }

        public override void Write(Utf8JsonWriter writer, SubscriptionVO value, JsonSerializerOptions options)
        {
            writer.WriteStartObject();

            writer.WriteString("date", value.Date.ToString("yyyy-MM-dd"));

            writer.WritePropertyName("train");
            var trainOptions = new JsonSerializerOptions(options)
            {
                Converters = { new TrainVOConverter() }
            };
            JsonSerializer.Serialize(writer, value.Train, trainOptions);

            writer.WriteEndObject();
        }
    }
}
