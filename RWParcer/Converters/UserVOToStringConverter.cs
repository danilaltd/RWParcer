using RWParcerCore.Domain.ValueObjects;
using RWParcerCore.InterfaceAdapters.Facades;

namespace RWParcer.Converters
{
    public static class UserVOToStringConverter
    {
        public static string Convert(UserVO user, IFacade facade)
        {
            string name = user.IsModerator ? "Модератор" : "Пользователь";
            string id = "Id: " + user.Id;
            string minUpdateInterval = $"Минимальный интервал обновления {user.MinUpdateInterval}";
            string maxSubscriptions = $"Максимальное количество подписок {user.MaxSubscriptions}";
            string isBlocked = user.IsBlocked ? "Заблокирован" : "";
            string lastActivity = $"Последняя активность: {user.LastActivity.ToString()}";
            return string.Join("\n", new[] { name, id, minUpdateInterval, maxSubscriptions, isBlocked, lastActivity }.Where(s => !string.IsNullOrEmpty(s)));
        }
    }
}
