using RWParcerCore.Domain.ValueObjects;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RWParcerCore.Infrastructure.Converters
{
    internal class TrainVOConverter : JsonConverter<TrainVO>
    {
        public override TrainVO Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            using var jsonDoc = JsonDocument.ParseValue(ref reader);
            var root = jsonDoc.RootElement;

            // Extract simple fields from JSON (CamelCase)
            string trainType = GetStringProperty(root, "trainType");
            string trainNumber = GetStringProperty(root, "trainNumber");
            string titleStationFrom = GetStringProperty(root, "titleStationFrom");
            string titleStationTo = GetStringProperty(root, "titleStationTo");
            string trainDays = GetStringProperty(root, "trainDays");
            string trainDaysExcept = GetStringProperty(root, "trainDaysExcept");

            // Extract StationFrom and StationTo
            var stationFromJson = GetProperty(root, "stationFrom");
            string fromStationLabel = GetStringProperty(stationFromJson, "label");
            string fromStationExp = GetStringProperty(stationFromJson, "exp");

            var stationToJson = GetProperty(root, "stationTo");
            string toStationLabel = GetStringProperty(stationToJson, "label");
            string toStationExp = GetStringProperty(stationToJson, "exp");

            // Parse fromTime and toTime
            string fromTimeStr = GetStringProperty(root, "fromTime");
            if (!TimeOnly.TryParse(fromTimeStr, out var fromTimeParsed))
                throw new JsonException($"Invalid time format for fromTime: {fromTimeStr}");
            long fromTime = DateTimeOffset.Parse($"1970-01-01 {fromTimeStr}").ToUnixTimeSeconds();

            string toTimeStr = GetStringProperty(root, "toTime");
            if (!TimeOnly.TryParse(toTimeStr, out var toTimeParsed))
                throw new JsonException($"Invalid time format for toTime: {toTimeStr}");
            long toTime = DateTimeOffset.Parse($"1970-01-01 {toTimeStr}").ToUnixTimeSeconds();

            // Extract durationMinutes
            if (!root.TryGetProperty("durationMinutes", out var durationMinutesElement))
                throw new JsonException("Property 'durationMinutes' not found.");

            if (durationMinutesElement.ValueKind != JsonValueKind.Number)
                throw new JsonException($"Expected 'durationMinutes' to be a number, but got {durationMinutesElement.ValueKind}.");

            if (!durationMinutesElement.TryGetUInt32(out uint durationMinutes))
                throw new JsonException($"Invalid value for durationMinutes: {durationMinutesElement}");

            // Create TrainVO using the constructor
            return new TrainVO(
                trainType,
                trainNumber,
                titleStationFrom,
                titleStationTo,
                fromStationLabel, // Label for StationFrom
                toStationLabel,   // Label for StationTo
                fromTime,
                toTime,
                trainDays,
                trainDaysExcept,
                fromStationExp,
                toStationExp,
                durationMinutes
            );
        }

        public override void Write(Utf8JsonWriter writer, TrainVO value, JsonSerializerOptions options)
        {
            writer.WriteStartObject();

            // Serialize simple fields (CamelCase)
            writer.WriteString("trainType", value.TrainType);
            writer.WriteString("trainNumber", value.TrainNumber);
            writer.WriteString("titleStationFrom", value.TitleStationFrom);
            writer.WriteString("titleStationTo", value.TitleStationTo);
            writer.WriteString("trainDays", value.TrainDays);
            writer.WriteString("trainDaysExcept", value.TrainDaysExcept);

            // Serialize FromTime and ToTime as strings
            writer.WriteString("fromTime", value.FromTime.AddHours(-1).ToString("HH:mm:ss"));
            writer.WriteString("toTime", value.ToTime.AddHours(-1).ToString("HH:mm:ss"));

            // Serialize Duration as durationMinutes
            writer.WriteNumber("durationMinutes", (uint)value.Duration.TotalMinutes);

            // Serialize StationFrom
            writer.WritePropertyName("stationFrom");
            writer.WriteStartObject();
            writer.WriteString("label", value.StationFrom.Label);
            writer.WriteString("exp", value.StationFrom.Exp);
            writer.WriteEndObject();

            // Serialize StationTo
            writer.WritePropertyName("stationTo");
            writer.WriteStartObject();
            writer.WriteString("label", value.StationTo.Label);
            writer.WriteString("exp", value.StationTo.Exp);
            writer.WriteEndObject();

            writer.WriteEndObject();
        }

        private static string GetStringProperty(JsonElement element, string propertyName)
        {
            if (!element.TryGetProperty(propertyName, out var property))
                throw new JsonException($"Property '{propertyName}' not found.");
            return property.GetString()!;
        }

        private static JsonElement GetProperty(JsonElement element, string propertyName)
        {
            if (!element.TryGetProperty(propertyName, out var property))
                throw new JsonException($"Property '{propertyName}' not found.");
            return property;
        }
    }
}
