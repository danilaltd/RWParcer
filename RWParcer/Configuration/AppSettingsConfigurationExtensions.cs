using System.Text;
using Microsoft.Extensions.Configuration;

namespace RWParcer.Configuration
{
    public static class AppSettingsConfigurationExtensions
    {
        public static IConfigurationBuilder AddAppSettings(this IConfigurationBuilder configurationBuilder)
        {
            var appSettingsJson = Environment.GetEnvironmentVariable("APPSETTINGS_JSON");

            if (!string.IsNullOrWhiteSpace(appSettingsJson))
            {
                using var stream = new MemoryStream(Encoding.UTF8.GetBytes(appSettingsJson));
                configurationBuilder.AddJsonStream(stream);
            }
            else
            {
                throw new FileNotFoundException("APPSETTINGS_JSON must be set");
            }

            configurationBuilder.AddEnvironmentVariables();
            return configurationBuilder;
        }
    }
}
