using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Interfaces;


namespace RWParcerCore.Infrastructure
{
    internal class AppDbContextFactory(DbContextOptions<AppDbContext> options, ILogger logger) : IAppDbContextFactory
    {
        private readonly DbContextOptions<AppDbContext> _options = options;
        private readonly ILogger _logger = logger;

        public AppDbContext CreateDbContext()
            => new(_options, _logger);
    }
}
