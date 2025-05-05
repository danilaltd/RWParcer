namespace RWParcer
{
    public enum CommandNames
    {
        Start,
        MainMenuSelect,
        FromSelect,
            ToSelect,
                TrainSelect,

                TrainMenuSelect,
        
        SubscribeDateSelect,
            SubscribeEnterDate,
        SubscribeEnterDateRange,
        SubscribeUseLastDate,

        UnsubscribeDateSelect,
            UnsubscribeEnterDate,
        UnsubscribeEnterDateRange,
        UnsubscribeUseLastDate,

            AddToFavorites,
            RemoveFromFavorites,



        FavoritesSelect,

        SubscriptionsSelect,
            SubscriptionMenuSelect,

        UnsubscribeSubscription,

        ModeratorMenuSelect,
        SelectUser,
        ModeratorEnterSpan,
        ManageUserMenuSelect,

        SendMessageEnterMessage,
        ChangeUserMinIntervalLimit,
        ChangeUserMaxSubscribtionLimit,
        BanUser,
        UnbanUser,
        PromoteUser,
        DemoteUser,
        ViewAllMessages,
        ViewMessages,

        GetStatus,
        Feedback,

        Unknown,
    }

}