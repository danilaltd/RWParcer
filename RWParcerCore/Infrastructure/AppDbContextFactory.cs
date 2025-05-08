using Microsoft.EntityFrameworkCore;

namespace RWParcerCore.Infrastructure
{
    internal class AppDbContextFactory : IAppDbContextFactory
    {
        private readonly DbContextOptions<AppDbContext> _options;

        public AppDbContextFactory(DbContextOptions<AppDbContext> options)
        {
            _options = options;
        }

        public AppDbContext CreateDbContext()
            => new AppDbContext();
    }
}
