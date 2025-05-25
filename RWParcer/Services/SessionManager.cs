using RWParcer.Interfaces;
using System.Collections.Concurrent;

namespace RWParcer
{
    public class SessionManager : ISessionManager
    {
        private readonly ConcurrentDictionary<string, UserSession> _store;

        public SessionManager()
        {
            _store = new ConcurrentDictionary<string, UserSession>();
        }

        public SessionManager(ConcurrentDictionary<string, UserSession> store)
        {
            _store = store;
        }

        public UserSession GetSession(string chatId) => _store.GetOrAdd(chatId, _ => new UserSession());

        public IReadOnlyDictionary<string, UserSession> GetAllSessions() => _store;
    }
}
