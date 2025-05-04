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

        ManageUsers,
        ModeratorEnterSpan,
        ManageUserMenuSelect,

        ChangeUserMinIntervalLimit,
        ChangeUserMaxSubscribtionLimit,
        BanUser,
        UnbanUser,
        PromoteUser,
        DemoteUser,

        GetStatus,
        Feedback,

        Unknown,
    }

}