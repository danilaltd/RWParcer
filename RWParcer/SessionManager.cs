using RWParcer.Interfaces;
using System.Collections.Concurrent;

namespace RWParcer
{
    public class SessionManager : ISessionManager
    {
        private readonly ConcurrentDictionary<string, UserSession> _store = new();
        public UserSession GetSession(string chatId) => _store.GetOrAdd(chatId, _ => new UserSession());
    }
}
