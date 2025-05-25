using System.Text.Json;
using System.Text.Json.Serialization;
using RWParcerCore.Domain.Interfaces;
using RWParcerCore.Infrastructure.Converters;

namespace RWParcerCore.Application.UseCases
{
    public class JsonOperationsUseCase : IJsonOperationsUseCase
    {
        private readonly JsonSerializerOptions _jsonOptions;

        public JsonOperationsUseCase()
        {
            _jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                WriteIndented = false,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
                Converters = { new TrainVOConverter(), new SubscriptionVOConverter(), new CarVOConverter(),  new MessageVOConverter(), new RouteVOConverter(), new StationVOConverter(), new UserVOConverter()}
            };
        }

        public string SerializeToJson(object obj)
        {
            return JsonSerializer.Serialize(obj, _jsonOptions);
        }

        public T? DeserializeFromJson<T>(string json)
        {
            return JsonSerializer.Deserialize<T>(json, _jsonOptions);
        }
    }
} 