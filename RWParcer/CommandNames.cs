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
            //SubscribeEnterRange,
            //SubscribeUseLastDate,

        UnsubscribeDateSelect,
            UnsubscribeEnterDate,
            //UnsubscribeEnterRange,
            //UnsubscribeUseLastDate,

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