using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Interfaces;


namespace RWParcerCore.Infrastructure
{
    internal class AppDbContextFactory : IAppDbContextFactory
    {
        private readonly DbContextOptions<AppDbContext> _options;
        private readonly ILogger _logger; 


        public AppDbContextFactory(DbContextOptions<AppDbContext> options, ILogger logger)
        {
            _options = options;
            _logger = logger;
        }

        public AppDbContext CreateDbContext()
            => new AppDbContext(_logger);
    }
}
