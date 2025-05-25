using Microsoft.EntityFrameworkCore;

namespace RWParcer
{
    public class SessionDbContextFactory
    {
        private readonly DbContextOptions<SessionDbContext> _options;

        public SessionDbContextFactory(DbContextOptions<SessionDbContext> options)
        {
            _options = options;
        }

        public SessionDbContext CreateDbContext()
            => new(_options);
    }
} 