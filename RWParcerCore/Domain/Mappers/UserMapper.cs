using RWParcerCore.Domain.Entities;
using RWParcerCore.Domain.ValueObjects;

namespace RWParcerCore.Domain.Mappers
{
    internal static class UserMapper
    {
        public static UserVO FromEntity(User user) => new(
            id: user.Id,
            isModerator: user.IsModerator,
            maxSubscriptions: user.MaxSubscriptions,
            minSubscriptionsInterval: user.MinSubscriptionsInterval,
            isBlocked: user.IsBlocked,
            lastActivity: user.LastActivity
        );
    }
}
