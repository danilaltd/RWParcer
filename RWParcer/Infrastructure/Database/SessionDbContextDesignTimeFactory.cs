using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Design;
using Microsoft.Extensions.Configuration;
using RWParcer.Settings;

namespace RWParcer
{
    public class SessionDbContextDesignTimeFactory : IDesignTimeDbContextFactory<SessionDbContext>
    {
        public SessionDbContext CreateDbContext(string[] args)
        {
            var configuration = new ConfigurationBuilder()
                .SetBasePath(Directory.GetCurrentDirectory())
                .AddJsonFile("appsettings.json")
                .Build();

            var settings = new DatabaseSettings();
            configuration.GetSection("DatabaseSettings").Bind(settings);

            var optionsBuilder = new DbContextOptionsBuilder<SessionDbContext>();
            optionsBuilder.UseNpgsql(settings.SessionConnectionString);

            return new SessionDbContext(optionsBuilder.Options);
        }
    }
} 