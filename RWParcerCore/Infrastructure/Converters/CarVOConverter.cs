using RWParcerCore.Domain.ValueObjects;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RWParcerCore.Infrastructure.Converters
{
    internal class CarVOConverter : JsonConverter<CarVO>
    {
        public override CarVO Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            using var jsonDoc = JsonDocument.ParseValue(ref reader);
            var root = jsonDoc.RootElement;

            // Extract type
            if (!root.TryGetProperty("type", out var typeElement))
                throw new JsonException("Property 'type' not found.");
            string typeStr = typeElement.GetString()!;
            if (!Enum.TryParse<CarType>(typeStr, true, out var carType))
                throw new JsonException($"Invalid CarType value: {typeStr}");

            // Extract number
            if (!root.TryGetProperty("number", out var numberElement))
                throw new JsonException("Property 'number' not found.");
            if (!numberElement.TryGetUInt32(out uint number))
                throw new JsonException($"Invalid number value: {numberElement}");

            // Extract freeSeats
            if (!root.TryGetProperty("freeSeats", out var freeSeatsElement))
                throw new JsonException("Property 'freeSeats' not found.");
            if (freeSeatsElement.ValueKind != JsonValueKind.Array)
                throw new JsonException("Expected 'freeSeats' to be an array.");
            var freeSeats = new List<uint>();
            foreach (var seat in freeSeatsElement.EnumerateArray())
            {
                if (!seat.TryGetUInt32(out uint seatNumber))
                    throw new JsonException($"Invalid seat number: {seat}");
                freeSeats.Add(seatNumber);
            }

            return new CarVO(carType, number, freeSeats);
        }

        public override void Write(Utf8JsonWriter writer, CarVO value, JsonSerializerOptions options)
        {
            writer.WriteStartObject();

            // Serialize type as string
            writer.WriteString("type", value.Type.ToString());

            // Serialize number
            writer.WriteNumber("number", value.Number);

            // Serialize freeSeats as array
            writer.WritePropertyName("freeSeats");
            writer.WriteStartArray();
            foreach (var seat in value.FreeSeats)
            {
                writer.WriteNumberValue(seat);
            }
            writer.WriteEndArray();

            writer.WriteEndObject();
        }
    }
}
