using RWParcerCore.Domain.Interfaces;

namespace RWParcerCore.Infrastructure.Logging
{
    public class ConsoleLogger : ILogger
    {
        public void LogError(Exception ex, string message, params object[] args)
        {
            Console.WriteLine($"[ERROR] {string.Format(message, args)}");
            if (ex != null)
            {
                Console.WriteLine($"Exception: {ex.Message}");
                Console.WriteLine($"Stack Trace: {ex.StackTrace}");
            }
        }

        public void LogWarning(string message, params object[] args)
        {
            Console.WriteLine($"[WARNING] {string.Format(message, args)}");
        }

        public void LogInfo(string message, params object[] args)
        {
            Console.WriteLine($"[INFO] {string.Format(message, args)}");
        }

        public void LogDebug(string message, params object[] args)
        {
            Console.WriteLine($"[DEBUG] {string.Format(message, args)}");
        }
    }
}