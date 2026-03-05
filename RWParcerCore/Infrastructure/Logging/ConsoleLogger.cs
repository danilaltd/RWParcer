using RWParcerCore.Domain.Interfaces;

namespace RWParcerCore.Infrastructure.Logging
{
    public class ConsoleLogger : ILogger
    {
        private string Now() => DateTime.UtcNow.ToString("yyyy-MM-dd HH:mm:ss.fff");
        public void LogError(Exception ex, string message, params object[] args)
        {
            Console.WriteLine($"{Now()} [ERROR] {string.Format(message, args)}");
            if (ex != null)
            {
                Console.WriteLine($"{Now()} Exception: {ex.Message}");
                Console.WriteLine($"{Now()} Stack Trace: {ex.StackTrace}");
            }
        }

        public void LogWarning(string message, params object[] args)
        {
            Console.WriteLine($"{Now()} [WARNING] {string.Format(message, args)}");
        }

        public void LogInfo(string message, params object[] args)
        {
            Console.WriteLine($"{Now()} [INFO] {string.Format(message, args)}");
        }

        public void LogDebug(string message, params object[] args)
        {
            Console.WriteLine($"{Now()} [DEBUG] {string.Format(message, args)}");
        }
    }
}