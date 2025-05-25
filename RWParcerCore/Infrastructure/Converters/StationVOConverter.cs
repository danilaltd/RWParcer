using RWParcerCore.Domain.ValueObjects;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RWParcerCore.Infrastructure.Converters
{
    internal class StationVOConverter : JsonConverter<StationVO>
    {
        public override StationVO Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            using var jsonDoc = JsonDocument.ParseValue(ref reader);
            var root = jsonDoc.RootElement;

            // Extract label
            if (!root.TryGetProperty("label", out var labelElement))
                throw new JsonException("Property 'label' not found.");
            string label = labelElement.GetString()!;

            // Extract exp
            if (!root.TryGetProperty("exp", out var expElement))
                throw new JsonException("Property 'exp' not found.");
            string exp = expElement.GetString()!;

            return new StationVO(label, exp);
        }

        public override void Write(Utf8JsonWriter writer, StationVO value, JsonSerializerOptions options)
        {
            writer.WriteStartObject();

            writer.WriteString("label", value.Label);
            writer.WriteString("exp", value.Exp);

            writer.WriteEndObject();
        }
    }
} 