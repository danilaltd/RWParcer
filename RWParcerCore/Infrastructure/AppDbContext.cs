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
                DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull,
                Converters = { new TrainVOConverter(), new SubscriptionVOConverter(), new CarVOConverter() }
            };

            // Configure Subscription entity
            modelBuilder.Entity<Subscription>()
                .Property(s => s.Details)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, jsonOptions),
                    v => DeserializeSubscriptionVO(v, jsonOptions)
                )
                .HasColumnType("TEXT");

            modelBuilder.Entity<Subscription>()
                .Property(s => s.LastState)
                .HasConversion(
                    v => JsonSerializer.Serialize(v, jsonOptions),
                    v => JsonSerializer.Deserialize<List<CarVO>>(v, jsonOptions) ?? new()
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

            // Add index on UserId for Favorite
            modelBuilder.Entity<Favorite>()
                .HasIndex(f => f.UserId);
        }

        // Helper methods for deserialization with error handling
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


    }

    internal class CarVOConverter : JsonConverter<CarVO>
    {
        public override CarVO Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        {
            using var jsonDoc = JsonDocument.ParseValue(ref reader);
            var root = jsonDoc.RootElement;

            // Extract type
            if (!root.TryGetProperty("type", out var typeElement))
                throw new JsonException("Property 'type' not found.");
            string typeStr = typeElement.GetString()!;
            if (!Enum.TryParse<CarType>(typeStr, true, out var carType))
                throw new JsonException($"Invalid CarType value: {typeStr}");

            // Extract number
            if (!root.TryGetProperty("number", out var numberElement))
                throw new JsonException("Property 'number' not found.");
            if (!numberElement.TryGetUInt32(out uint number))
                throw new JsonException($"Invalid number value: {numberElement}");

            // Extract freeSeats
            if (!root.TryGetProperty("freeSeats", out var freeSeatsElement))
                throw new JsonException("Property 'freeSeats' not found.");
            if (freeSeatsElement.ValueKind != JsonValueKind.Array)
                throw new JsonException("Expected 'freeSeats' to be an array.");
            var freeSeats = new List<uint>();
            foreach (var seat in freeSeatsElement.EnumerateArray())
            {
                if (!seat.TryGetUInt32(out uint seatNumber))
                    throw new JsonException($"Invalid seat number: {seat}");
                freeSeats.Add(seatNumber);
            }

            return new CarVO(carType, number, freeSeats);
        }

        public override void Write(Utf8JsonWriter writer, CarVO value, JsonSerializerOptions options)
        {
            writer.WriteStartObject();

            // Serialize type as string
            writer.WriteString("type", value.Type.ToString());

            // Serialize number
            writer.WriteNumber("number", value.Number);

            // Serialize freeSeats as array
            writer.WritePropertyName("freeSeats");
            writer.WriteStartArray();
            foreach (var seat in value.FreeSeats)
            {
                writer.WriteNumberValue(seat);
            }
            writer.WriteEndArray();

            writer.WriteEndObject();
        }
    }
}
