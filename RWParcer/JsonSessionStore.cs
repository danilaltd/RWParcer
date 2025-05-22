using Microsoft.Extensions.Options;
using Newtonsoft.Json;
using RWParcer.Interfaces;

namespace RWParcer
{
    public class JsonSessionStore : ISessionStore
    {
        private readonly string _path;
        private readonly JsonSerializerSettings _settings;
        private readonly SemaphoreSlim _saveLock = new(1, 1);

        public JsonSessionStore(IOptions<BotSettings> options)
        {
            _path = options.Value.SessionFilePath;
            _settings = new JsonSerializerSettings
            {
                TypeNameHandling = TypeNameHandling.All,
                PreserveReferencesHandling = PreserveReferencesHandling.All,
                Formatting = Formatting.Indented,
                ContractResolver = new PrivateFieldsAndBypassCtorResolver()
            };
        }

        public ISessionManager Load()
        {
            if (!File.Exists(_path))
                return new SessionManager();

            var json = File.ReadAllText(_path);
            return JsonConvert.DeserializeObject<SessionManager>(json, _settings)!;
        }

        public void Save(ISessionManager sessions)
            => SaveAsync(sessions).GetAwaiter().GetResult();  // на всякий случай

        public Task SaveAsync(ISessionManager sessions)
        {
            return Task.CompletedTask;
            //var json = JsonConvert.SerializeObject(sessions, _settings);
            //var tmpFile = _path + ".tmp";

            //await _saveLock.WaitAsync();
            //try
            //{
            //    // 1) Асинхронно пишем в временный файл
            //    await File.WriteAllTextAsync(tmpFile, json).ConfigureAwait(false);

            //    // 2) Синхронная атомарная замена
            //    File.Replace(tmpFile, _path, null);
            //}
            //finally
            //{
            //    _saveLock.Release();
            //}
        }
    }
}