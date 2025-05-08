using Microsoft.EntityFrameworkCore;
using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.Infrastructure.Converters;
using System.Diagnostics;
using System.Text;
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

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {
            if (!optionsBuilder.IsConfigured)
            {
                // Используем Npgsql для подключения к Supabase (PostgreSQL)
                optionsBuilder.UseNpgsql("User Id=postgres.phzzfofwodzqkppnmjzq;Password=mypswhelloworl;Server=aws-0-eu-north-1.pooler.supabase.com;Port=5432;Database=postgres");
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

            // Конфигурация сущности Subscription
            modelBuilder.Entity<Subscription>()
                .Property(s => s.Details)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, jsonOptions),
                    v => DeserializeSubscriptionVO(v, jsonOptions)
                )
                .HasColumnType("jsonb"); // Изменено на jsonb для PostgreSQL

            modelBuilder.Entity<Subscription>()
                .Property(s => s.LastState)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, jsonOptions),
                    v => JsonSerializer.Deserialize<List<CarVO>>(v, jsonOptions) ?? new()
                )
                .HasColumnType("jsonb"); // Изменено на jsonb для PostgreSQL

            modelBuilder.Entity<Subscription>()
                .HasIndex(s => s.UserId);

            // Конфигурация сущности Favorite
            modelBuilder.Entity<Favorite>()
                .Property(f => f.TrainInfo)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, jsonOptions),
                    v => DeserializeTrainVO(v, jsonOptions)
                )
                .HasColumnType("jsonb"); // Изменено на jsonb для PostgreSQL

            modelBuilder.Entity<Favorite>()
                .HasIndex(f => f.UserId);

            // Настройка именования в формате snake_case для совместимости с PostgreSQL
            foreach (var entity in modelBuilder.Model.GetEntityTypes())
            {
                entity.SetTableName(ToSnakeCase(entity.GetTableName()));
                foreach (var property in entity.GetProperties())
                {
                    property.SetColumnName(ToSnakeCase(property.GetColumnName()));
                }
                foreach (var key in entity.GetKeys())
                {
                    key.SetName(ToSnakeCase(key.GetName()));
                }
                foreach (var foreignKey in entity.GetForeignKeys())
                {
                    foreignKey.SetConstraintName(ToSnakeCase(foreignKey.GetConstraintName()));
                }
                foreach (var index in entity.GetIndexes())
                {
                    index.SetDatabaseName(ToSnakeCase(index.GetDatabaseName()));
                }
            }
        }

        // Вспомогательные методы десериализации с обработкой ошибок
        private static SubscriptionVO DeserializeSubscriptionVO(string json, JsonSerializerOptions jsonOptions)
        {
            try
            {
                return JsonSerializer.Deserialize<SubscriptionVO>(json, jsonOptions)
                    ?? new SubscriptionVO(new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", "", 0), DateOnly.FromDateTime(DateTime.Now));
            }
            catch (JsonException ex)
            {
                Debug.WriteLine($"Deserialization error for SubscriptionVO: {ex.Message}");
                return new SubscriptionVO(new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", "", 0), DateOnly.FromDateTime(DateTime.Now));
            }
        }

        private static TrainVO DeserializeTrainVO(string json, JsonSerializerOptions jsonOptions)
        {
            try
            {
                return JsonSerializer.Deserialize<TrainVO>(json, jsonOptions)
                    ?? new TrainVO("default", "0", "", "", "", "", 0, 0, "", "", "", "", 0);
            }
            catch (JsonException ex)
            {
                Debug.WriteLine($"Deserialization error for TrainVO: {ex.Message}");
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