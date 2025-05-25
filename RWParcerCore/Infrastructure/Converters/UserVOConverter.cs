using RWParcerCore.Domain.ValueObjects;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RWParcerCore.Infrastructure.Converters
{
    internal class UserVOConverter : JsonConverter<UserVO>
    {
        public override UserVO Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            using var jsonDoc = JsonDocument.ParseValue(ref reader);
            var root = jsonDoc.RootElement;

            // Extract id
            if (!root.TryGetProperty("id", out var idElement))
                throw new JsonException("Property 'id' not found.");
            string id = idElement.GetString()!;

            // Extract isModerator
            if (!root.TryGetProperty("isModerator", out var isModeratorElement))
                throw new JsonException("Property 'isModerator' not found.");
            bool isModerator;
            try
            {
                isModerator = isModeratorElement.GetBoolean();
            }
            catch (InvalidOperationException)
            {
                throw new JsonException($"Invalid boolean value for isModerator: {isModeratorElement}");
            }


            // Extract maxSubscriptions
            if (!root.TryGetProperty("maxSubscriptions", out var maxSubscriptionsElement))
                throw new JsonException("Property 'maxSubscriptions' not found.");
            if (!maxSubscriptionsElement.TryGetUInt32(out uint maxSubscriptions))
                throw new JsonException($"Invalid value for maxSubscriptions: {maxSubscriptionsElement}");

            // Extract minSubscriptionsInterval
            if (!root.TryGetProperty("minSubscriptionsInterval", out var minSubscriptionsIntervalElement))
                throw new JsonException("Property 'minSubscriptionsInterval' not found.");
            if (!minSubscriptionsIntervalElement.TryGetUInt32(out uint minSubscriptionsInterval))
                throw new JsonException($"Invalid value for minSubscriptionsInterval: {minSubscriptionsIntervalElement}");

            // Extract isBlocked
            if (!root.TryGetProperty("isBlocked", out var isBlockedElement))
                throw new JsonException("Property 'isBlocked' not found.");
            bool isBlocked;
            try
            {
                isBlocked = isBlockedElement.GetBoolean();
            }
            catch (InvalidOperationException)
            {
                throw new JsonException($"Invalid boolean value for isBlocked: {isBlockedElement}");
            }


            // Extract lastActivity
            if (!root.TryGetProperty("lastActivity", out var lastActivityElement))
                throw new JsonException("Property 'lastActivity' not found.");
            string lastActivityStr = lastActivityElement.GetString()!;
            if (!DateTime.TryParse(lastActivityStr, out DateTime lastActivity))
                throw new JsonException($"Invalid date format for lastActivity: {lastActivityStr}");

            return new UserVO(id, isModerator, maxSubscriptions, minSubscriptionsInterval, isBlocked, lastActivity);
        }

        public override void Write(Utf8JsonWriter writer, UserVO value, JsonSerializerOptions options)
        {
            writer.WriteStartObject();

            writer.WriteString("id", value.Id);
            writer.WriteBoolean("isModerator", value.IsModerator);
            writer.WriteNumber("maxSubscriptions", value.MaxSubscriptions);
            writer.WriteNumber("minSubscriptionsInterval", value.MinUpdateInterval);
            writer.WriteBoolean("isBlocked", value.IsBlocked);
            writer.WriteString("lastActivity", value.LastActivity.ToString("yyyy-MM-ddTHH:mm:ss"));

            writer.WriteEndObject();
        }
    }
} 