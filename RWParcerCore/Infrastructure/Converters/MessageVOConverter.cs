using RWParcerCore.Domain.ValueObjects;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RWParcerCore.Infrastructure.Converters
{
    internal class MessageVOConverter : JsonConverter<MessageVO>
    {
        public override MessageVO Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            using var jsonDoc = JsonDocument.ParseValue(ref reader);
            var root = jsonDoc.RootElement;

            // Extract senderId
            if (!root.TryGetProperty("senderId", out var senderIdElement))
                throw new JsonException("Property 'senderId' not found.");
            string senderId = senderIdElement.GetString()!;

            // Extract receiverId
            if (!root.TryGetProperty("receiverId", out var receiverIdElement))
                throw new JsonException("Property 'receiverId' not found.");
            string receiverId = receiverIdElement.GetString()!;

            // Extract content
            if (!root.TryGetProperty("content", out var contentElement))
                throw new JsonException("Property 'content' not found.");
            string content = contentElement.GetString()!;

            // Extract sentDate
            if (!root.TryGetProperty("sentDate", out var sentDateElement))
                throw new JsonException("Property 'sentDate' not found.");
            string sentDateStr = sentDateElement.GetString()!;
            if (!DateTime.TryParse(sentDateStr, out DateTime sentDate))
                throw new JsonException($"Invalid date format: {sentDateStr}");

            return new MessageVO(senderId, receiverId, content, sentDate);
        }

        public override void Write(Utf8JsonWriter writer, MessageVO value, JsonSerializerOptions options)
        {
            writer.WriteStartObject();

            writer.WriteString("senderId", value.SenderId);
            writer.WriteString("receiverId", value.ReceiverId);
            writer.WriteString("content", value.Content);
            writer.WriteString("sentDate", value.SentDate.ToString("yyyy-MM-ddTHH:mm:ss"));

            writer.WriteEndObject();
        }
    }
} 