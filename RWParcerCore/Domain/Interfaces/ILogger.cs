namespace RWParcerCore.Domain.Interfaces
{
    public interface ILogger
    {
        void LogError(Exception ex, string message, params object[] args);
        void LogWarning(string message, params object[] args);
        void LogInfo(string message, params object[] args);
        void LogDebug(string message, params object[] args);
    }
} 