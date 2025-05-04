using RWParcerCore.Domain.ValueObjects;

namespace RWParcer.Converters
{
    public static class SubscriptionVOToStringConverter
    {
        public static string Convert(SubscriptionVO subscription)
        {
            var train = subscription.Train;
            string date = subscription.Date.ToString("dd.MM.yyyy");
            string type = train.TrainType;
            string number =  "№" + train.TrainNumber;
            string times = $"{train.FromTime:HH:mm}→{train.ToTime:HH:mm}";

            string trainDays = "Дни курсирования: " + train.TrainDays;
            if (train.TrainDaysExcept.Length != 0)
            {
                trainDays += ", кроме " + train.TrainDaysExcept;
            }

            return string.Join("\n", date, '\n', type, number, times, trainDays);
        }
    }
}
