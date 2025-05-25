using Microsoft.EntityFrameworkCore;

namespace RWParcer
{
    public class SessionDbContext : DbContext
    {
        public DbSet<SessionEntity> Sessions { get; set; }

        public SessionDbContext(DbContextOptions<SessionDbContext> options) : base(options)
        {
        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            modelBuilder.Entity<SessionEntity>(entity =>
            {
                entity.HasKey(e => e.ChatId);
                entity.Property(e => e.ChatId).IsRequired();
                entity.Property(e => e.Data).HasColumnType("TEXT");
            });
        }
    }

    public class SessionEntity(string chatId, CommandNames? currentCommand, bool initState, string data, DateOnly date)
    {
        public string ChatId { get; private set; } = chatId;
        public CommandNames? CurrentCommand { get; private set; } = currentCommand;
        public bool InitState { get; private set; } = initState;
        public string Data { get; private set; } = data;
        public DateOnly Date { get; private set; } = date;
    }
} 