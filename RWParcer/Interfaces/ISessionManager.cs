namespace RWParcer.Interfaces
{
    public interface ISessionManager
    {
        UserSession GetSession(string chatId);
    }
}