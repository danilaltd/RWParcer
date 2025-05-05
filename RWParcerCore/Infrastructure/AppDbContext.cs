using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.Infrastructure.Converters;
using System.Diagnostics;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RWParcerCore.Infrastructure
{
    internal class AppDbContext : DbContext
    {
        public DbSet<Favorite> Favorites { get; set; }
        public DbSet<Message> Messages { get; set; }
        public DbSet<Notification> Notifications { get; set; }
        public DbSet<Subscription> Subscriptions { get; set; }
        public DbSet<User> Users { get; set; }

        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
            Database.EnsureCreated();
        }

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            if (!optionsBuilder.IsConfigured)
            {
                optionsBuilder.UseSqlite("Data Source=app.db");
            }
        }


        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            var jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                WriteIndented = false,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
            };

            modelBuilder.Entity<Subscription>()
                .Ignore(s => s.LastState)
                .Property(s => s.Details)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, jsonOptions),
                    v => DeserializeSubscriptionVO(v, jsonOptions)
                )
                .HasColumnType("TEXT");
            modelBuilder.Entity<Subscription>()
                .HasIndex(s => s.UserId);

            modelBuilder.Entity<Favorite>()
                .Property(f => f.TrainInfo)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, jsonOptions),
                    v => DeserializeTrainVO(v, jsonOptions)
                )
                .HasColumnType("TEXT");
            modelBuilder.Entity<Favorite>()
                .HasIndex(f => f.UserId);
        }

        private static SubscriptionVO DeserializeSubscriptionVO(string json, JsonSerializerOptions jsonOptions)
        {
            try
            {
                var deserializeOptions = new JsonSerializerOptions(jsonOptions)
                {
                    Converters = { new SubscriptionVOConverter() }
                };
                return JsonSerializer.Deserialize<SubscriptionVO>(json, deserializeOptions)
                    ?? new SubscriptionVO(
                        new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", ""),
                        DateOnly.FromDateTime(DateTime.Now)
                    );
            }
            catch (JsonException ex)
            {
                Debug.WriteLine($"Deserialization error for SubscriptionVO: {ex.Message}");
                return new SubscriptionVO(
                    new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", ""),
                    DateOnly.FromDateTime(DateTime.Now)
                );
            }
        }

        private static TrainVO DeserializeTrainVO(string json, JsonSerializerOptions jsonOptions)
        {
            try
            {
                var deserializeOptions = new JsonSerializerOptions(jsonOptions)
                {
                    Converters = { new TrainVOConverter() }
                };
                return JsonSerializer.Deserialize<TrainVO>(json, deserializeOptions)
                    ?? new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", "");
            }
            catch (JsonException ex)
            {
                Debug.WriteLine($"Deserialization error for TrainVO: {ex.Message}");
                return new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", "");
            }
        }


    }
}
