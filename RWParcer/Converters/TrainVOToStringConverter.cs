using RWParcerCore.Domain.ValueObjects;

namespace RWParcer.Converters
{
    public static class TrainVOToStringConverter
    {
        public static string Convert(TrainVO train)
        {
            string type = train.TrainType;
            string number =  "№" + train.TrainNumber;
            string times = $"{train.FromTime:HH:mm}→{train.ToTime:HH:mm}";

            string trainDays = "Дни курсирования: " + train.TrainDays;
            if (train.TrainDaysExcept.Length != 0)
            {
                trainDays += ", кроме " + train.TrainDaysExcept;
            }

            return string.Join("\n", type, number, times, trainDays);
        }
    }
}
