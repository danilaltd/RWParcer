namespace RWParcerCore.Domain.Interfaces
{
    public interface IJsonOperationsUseCase
    {
        string SerializeToJson(object obj);
        T? DeserializeFromJson<T>(string json);
    }
} 