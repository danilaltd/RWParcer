namespace RWParcer.Interfaces
{
    public interface ISessionStore
    {
        ISessionManager Load();
        void Save(ISessionManager sessions);
        Task SaveAsync(ISessionManager sessions);
    }
}