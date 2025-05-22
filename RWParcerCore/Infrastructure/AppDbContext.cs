using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Interfaces;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.Infrastructure.Converters;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace RWParcerCore.Infrastructure
{
    internal class AppDbContext : DbContext
    {
        private readonly ILogger _logger;
        public DbSet<Favorite> Favorites { get; set; }
        public DbSet<Message> Messages { get; set; }
        public DbSet<Notification> Notifications { get; set; }
        public DbSet<Subscription> Subscriptions { get; set; }
        public DbSet<User> Users { get; set; }
        public AppDbContext(DbContextOptions<AppDbContext> options, ILogger logger) : base(options)
        {
            _logger = logger;
        }
        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            if (!optionsBuilder.IsConfigured)
            {
                throw new Exception("No options in AppDbContext");
            }
        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            var jsonOptions = new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                WriteIndented = false,
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
                Converters = { new TrainVOConverter(), new SubscriptionVOConverter(), new CarVOConverter() }
            };

            modelBuilder.Entity<Subscription>()
                .Property(s => s.Details)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, jsonOptions),
                    v => DeserializeSubscriptionVO(v, jsonOptions)
                )
                .HasColumnType("jsonb"); 

            modelBuilder.Entity<Subscription>()
                .Property(s => s.LastState)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, jsonOptions),
                    v => JsonSerializer.Deserialize<List<CarVO>>(v, jsonOptions) ?? new()
                )
                .HasColumnType("jsonb");

            modelBuilder.Entity<Subscription>()
                .HasIndex(s => s.UserId);

            modelBuilder.Entity<Favorite>()
                .Property(f => f.TrainInfo)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, jsonOptions),
                    v => DeserializeTrainVO(v, jsonOptions)
                )
                .HasColumnType("jsonb");

            modelBuilder.Entity<Favorite>()
                .HasIndex(f => f.UserId);

            foreach (var entity in modelBuilder.Model.GetEntityTypes())
            {
                var tableName = entity.GetTableName();
                if (tableName != null)
                {
                    entity.SetTableName(ToSnakeCase(tableName));
                }

                foreach (var property in entity.GetProperties())
                {
                    var columnName = property.GetColumnName();
                    if (columnName != null)
                    {
                        property.SetColumnName(ToSnakeCase(columnName));
                    }
                }

                foreach (var key in entity.GetKeys())
                {
                    var keyName = key.GetName();
                    if (keyName != null)
                    {
                        key.SetName(ToSnakeCase(keyName));
                    }
                }

                foreach (var foreignKey in entity.GetForeignKeys())
                {
                    var constraintName = foreignKey.GetConstraintName();
                    if (constraintName != null)
                    {
                        foreignKey.SetConstraintName(ToSnakeCase(constraintName));
                    }
                }

                foreach (var index in entity.GetIndexes())
                {
                    var indexName = index.GetDatabaseName();
                    if (indexName != null)
                    {
                        index.SetDatabaseName(ToSnakeCase(indexName));
                    }
                }
            }
        }

        // Вспомогательные методы десериализации с обработкой ошибок
        private SubscriptionVO DeserializeSubscriptionVO(string json, JsonSerializerOptions jsonOptions)
        {
            try
            {
                return JsonSerializer.Deserialize<SubscriptionVO>(json, jsonOptions)
                    ?? new SubscriptionVO(new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", "", 0), DateOnly.FromDateTime(DateTime.Now));
            }
            catch (JsonException ex)
            {
                _logger.LogDebug($"Deserialization error for SubscriptionVO: {ex.Message}");
                return new SubscriptionVO(new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", "", 0), DateOnly.FromDateTime(DateTime.Now));
            }
        }

        private TrainVO DeserializeTrainVO(string json, JsonSerializerOptions jsonOptions)
        {
            try
            {
                return JsonSerializer.Deserialize<TrainVO>(json, jsonOptions)
                    ?? new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", "", 0);
            }
            catch (JsonException ex)
            {
                _logger.LogDebug($"Deserialization error for TrainVO: {ex.Message}");
                return new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", "", 0);
            }
        }

        // Метод для преобразования имен в snake_case
        private static string ToSnakeCase(string name)
        {
            if (string.IsNullOrEmpty(name)) return name;
            var sb = new StringBuilder();
            for (int i = 0; i < name.Length; i++)
            {
                if (i > 0 && char.IsUpper(name[i]))
                {
                    sb.Append('_');
                }
                sb.Append(char.ToLower(name[i]));
            }
            return sb.ToString();
        }
    }
}