using RWParcerCore.Domain.ValueObjects;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RWParcerCore.Infrastructure.Converters
{
    public class TrainVOConverter : JsonConverter<TrainVO>
    {
        public override TrainVO Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            using var jsonDoc = JsonDocument.ParseValue(ref reader);
            var root = jsonDoc.RootElement;

            // Извлекаем поля из JSON (CamelCase)
            if (!root.TryGetProperty("trainType", out var trainTypeElement))
                throw new JsonException("Property 'trainType' not found.");
            string trainType = trainTypeElement.GetString()!;

            if (!root.TryGetProperty("trainNumber", out var trainNumberElement))
                throw new JsonException("Property 'trainNumber' not found.");
            string trainNumber = trainNumberElement.GetString()!;

            if (!root.TryGetProperty("titleStationFrom", out var titleStationFromElement))
                throw new JsonException("Property 'titleStationFrom' not found.");
            string titleStationFrom = titleStationFromElement.GetString()!;

            if (!root.TryGetProperty("titleStationTo", out var titleStationToElement))
                throw new JsonException("Property 'titleStationTo' not found.");
            string titleStationTo = titleStationToElement.GetString()!;

            if (!root.TryGetProperty("trainDays", out var trainDaysElement))
                throw new JsonException("Property 'trainDays' not found.");
            string trainDays = trainDaysElement.GetString()!;

            if (!root.TryGetProperty("trainDaysExcept", out var trainDaysExceptElement))
                throw new JsonException("Property 'trainDaysExcept' not found.");
            string trainDaysExcept = trainDaysExceptElement.GetString()!;

            // Извлекаем StationFrom и StationTo
            if (!root.TryGetProperty("stationFrom", out var stationFromJson))
                throw new JsonException("Property 'stationFrom' not found.");
            string fromStationDb = stationFromJson.GetProperty("value").GetString()!;
            string fromStationExp = stationFromJson.GetProperty("label").GetString()!;

            if (!root.TryGetProperty("stationTo", out var stationToJson))
                throw new JsonException("Property 'stationTo' not found.");
            string toStationDb = stationToJson.GetProperty("value").GetString()!;
            string toStationExp = stationToJson.GetProperty("label").GetString()!;

            // Парсим время (fromTime и toTime)
            if (!root.TryGetProperty("fromTime", out var fromTimeElement))
                throw new JsonException("Property 'fromTime' not found.");
            string fromTimeStr = fromTimeElement.GetString()!;
            if (!TimeOnly.TryParse(fromTimeStr, out var fromTimeParsed))
                throw new JsonException($"Invalid time format for fromTime: {fromTimeStr}");
            long fromTime = DateTimeOffset.Parse($"1970-01-01 {fromTimeStr}").AddHours(-1).ToUnixTimeSeconds();

            if (!root.TryGetProperty("toTime", out var toTimeElement))
                throw new JsonException("Property 'toTime' not found.");
            string toTimeStr = toTimeElement.GetString()!;
            if (!TimeOnly.TryParse(toTimeStr, out var toTimeParsed))
                throw new JsonException($"Invalid time format for toTime: {toTimeStr}");
            long toTime = DateTimeOffset.Parse($"1970-01-01 {toTimeStr}").AddHours(-1).ToUnixTimeSeconds();

            // Создаём TrainVO через существующий конструктор
            return new TrainVO(
                trainType,
                trainNumber,
                titleStationFrom,
                titleStationTo,
                fromStationDb,
                toStationDb,
                fromTime,
                toTime,
                trainDays,
                trainDaysExcept,
                fromStationExp,
                toStationExp
            );
        }

        public override void Write(Utf8JsonWriter writer, TrainVO value, JsonSerializerOptions options)
        {
            writer.WriteStartObject();

            // Сериализуем простые поля (CamelCase)
            writer.WriteString("trainType", value.TrainType);
            writer.WriteString("trainNumber", value.TrainNumber);
            writer.WriteString("titleStationFrom", value.TitleStationFrom);
            writer.WriteString("titleStationTo", value.TitleStationTo);
            writer.WriteString("trainDays", value.TrainDays);
            writer.WriteString("trainDaysExcept", value.TrainDaysExcept);

            // Сериализуем FromTime и ToTime как строки

            writer.WriteString("fromTime", value.FromTime.ToString("HH:mm:ss"));
            writer.WriteString("toTime", value.ToTime.ToString("HH:mm:ss"));

            // Сериализуем StationFrom
            writer.WritePropertyName("stationFrom");
            writer.WriteStartObject();
            writer.WriteString("label", value.StationFrom.Label);
            writer.WriteString("value", value.StationFrom.Value);
            writer.WriteEndObject();

            // Сериализуем StationTo
            writer.WritePropertyName("stationTo");
            writer.WriteStartObject();
            writer.WriteString("label", value.StationTo.Label);
            writer.WriteString("value", value.StationTo.Value);
            writer.WriteEndObject();

            writer.WriteEndObject();
        }
    }
}
