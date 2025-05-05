using RWParcerCore.Domain.ValueObjects;

namespace RWParcer.Converters
{
    public static class SubscriptionVOToStringConverter
    {
        public static string Convert(SubscriptionVO subscription)
        {
            string date = subscription.Date.ToString("dd.MM.yyyy");

            return string.Join("\n", date, '\n', TrainVOToStringConverter.Convert(subscription.Train));
        }
    }
}
