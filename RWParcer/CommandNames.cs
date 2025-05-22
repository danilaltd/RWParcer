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
        ResetSubscription,

        ModeratorMenuSelect,
        SelectUser,
        ModeratorEnterSpan,
        ModeratorSpanDay,
        ModeratorSpanHour,
        ModeratorSpanMinute,
        ModeratorSpanSelect,
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