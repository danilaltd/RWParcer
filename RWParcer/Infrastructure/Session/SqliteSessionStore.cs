using Microsoft.EntityFrameworkCore;
using RWParcer.Infrastructure.Database;
using RWParcer.Interfaces;
using RWParcer.Models;
using RWParcer.Services;
using RWParcerCore.InterfaceAdapters.Facades;
using System.Collections.Concurrent;
using System.Text.Json;

namespace RWParcer.Infrastructure.Session
{
    public class SqliteSessionStore : ISessionStore
    {
        private readonly IFacade _facade;
        private readonly SemaphoreSlim _saveLock = new(1, 1);
        private readonly SessionDbContextFactory _dbContextFactory;

        public SqliteSessionStore(IFacade facade, SessionDbContextFactory dbContextFactory)
        {
            _facade = facade;
            _dbContextFactory = dbContextFactory;
        }

        public ISessionManager Load()
        {
            using var context = CreateContext();
            context.Database.EnsureCreated();

            var sessions = new ConcurrentDictionary<string, UserSession>();
            var entities = context.Sessions.ToList();

            foreach (var entity in entities)
            {
                if (string.IsNullOrEmpty(entity.Data))
                {
                    sessions[entity.ChatId] = new UserSession(entity.CurrentCommand, entity.InitState, [])
                    {
                        Date = entity.Date
                    };
                    continue;
                }

                try
                {
                    var jsonArray = JsonSerializer.Deserialize<List<JsonElement>>(entity.Data);
                    var data = new List<object>();
                    if (jsonArray != null)
                    {
                        foreach (var jsonItem in jsonArray)
                        {
                            var typeName = jsonItem.GetProperty("Type").GetString();
                            var jsonData = jsonItem.GetProperty("Data").GetString();
                            if (typeName != null && jsonData != null)
                            {
                                var type = Type.GetType(typeName);
                                if (type != null)
                                {
                                    var deserializeMethod = typeof(IFacade).GetMethod("DeserializeFromJson")
                                        ?.MakeGenericMethod(type);
                                    var item = deserializeMethod?.Invoke(_facade, [jsonData]);
                                    if (item != null)
                                    {
                                        data.Add(item);
                                    }
                                }
                            }
                        }
                    }
                    sessions[entity.ChatId] = new UserSession(entity.CurrentCommand, entity.InitState, data)
                    {
                        Date = entity.Date
                    };
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error deserializing session data for chat {entity.ChatId}: {ex.Message}");
                    sessions[entity.ChatId] = new UserSession(entity.CurrentCommand, entity.InitState, [])
                    {
                        Date = entity.Date
                    };
                }
            }

            return new SessionManager(sessions);
        }

        public void Save(ISessionManager sessions)
            => SaveAsync(sessions).GetAwaiter().GetResult();

        public async Task SaveAsync(ISessionManager sessions)
        {
            await _saveLock.WaitAsync();
            try
            {
                using var context = CreateContext();
                context.Database.EnsureCreated();

                var existingSessions = await context.Sessions.ToDictionaryAsync(s => s.ChatId);
                var sessionManager = (SessionManager)sessions;

                foreach (var kvp in sessionManager.GetAllSessions())
                {
                    var jsonObjects = kvp.Value.Data.Select(item => new
                    {
                        Type = item.GetType().AssemblyQualifiedName,
                        Data = _facade.SerializeToJson(item)
                    }).ToList();

                    var entity = new SessionEntity(kvp.Key, kvp.Value.CurrentCommand, kvp.Value.InitState, JsonSerializer.Serialize(jsonObjects), kvp.Value.Date);

                    if (existingSessions.ContainsKey(kvp.Key))
                    {
                        context.Entry(existingSessions[kvp.Key]).CurrentValues.SetValues(entity);
                    }
                    else
                    {
                        context.Sessions.Add(entity);
                    }
                }

                await context.SaveChangesAsync();
            }
            finally
            {
                _saveLock.Release();
            }
        }

        private SessionDbContext CreateContext()
        {
            return _dbContextFactory.CreateDbContext();
        }
    }
} 